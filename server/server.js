const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

dotenv.config({ path: path.join(__dirname, '.env') });

const app = express();
const port = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Serve Static Frontend Files
app.use(express.static(path.join(__dirname, '..', 'frontend')));

// Serve Output Files from Backend Output Directory
app.use('/output', express.static(path.join(__dirname, '..', 'backend', 'output')));

const storage = multer.memoryStorage();
const upload = multer({
    storage: storage,
    limits: { fileSize: 10 * 1024 * 1024 }
});

// Global Gemini Instance
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

/**
 * Main AI Banner Generation Proxy
 */
app.post('/generate-banner', upload.any(), async (req, res) => {
    try {
        const userPrompt = req.body.prompt;
        const userMode = req.body.mode || 'standard';
        const size = req.body.size || '1200x628';

        console.log(`\n[REQUEST] Mode: ${userMode.toUpperCase()}, Size: ${size}, Prompt: "${userPrompt}"`);

        // Helper to forward to Python (FastAPI on Port 8000)
        const forwardToPython = async (overrides = null) => {
            const formData = new FormData();
            Object.entries(req.body).forEach(([key, value]) => {
                if (key !== 'overrides') formData.append(key, value);
            });
            if (overrides) formData.append('overrides', JSON.stringify(overrides));

            // Forward files if any (logos, players) - if provided in req
            if (req.files) {
                for (const fieldname in req.files) {
                    req.files[fieldname].forEach(file => {
                        const blob = new Blob([file.buffer], { type: file.mimetype });
                        formData.append(fieldname, blob, file.originalname);
                    });
                }
            }

            const pyRes = await fetch('http://127.0.0.1:8000/generate-banner', {
                method: 'POST',
                body: formData
            });
            if (!pyRes.ok) throw new Error(`Python Backend Error: ${pyRes.statusText}`);
            return await pyRes.json();
        };

        // --- STEP 1: Basic Generation (Always start with base PSD render) ---
        const initialResult = await forwardToPython();
        console.log(`[Flow] Base Render Success: ${initialResult.imageUrl}`);

        // If Standard mode, return immediately (No AI)
        if (userMode === 'standard') {
            return res.json({
                ...initialResult,
                aiRefined: false,
                info: "Standard Base Render (No AI)"
            });
        }

        // --- STEP 2: AI Refinement (Optional) ---
        if (!userPrompt || userPrompt.trim().length === 0) {
            return res.json({
                ...initialResult,
                aiRefined: false,
                info: "No prompt provided. Showing base render."
            });
        }

        try {
            // Fetch the base image for AI vision models
            const baseImageUrl = `http://127.0.0.1:8000${initialResult.imageUrl}`;
            const imgResponse = await fetch(baseImageUrl);
            const imgBuffer = Buffer.from(await imgResponse.arrayBuffer());

            const userModel = req.body.model || 'gemini-3-pro-image-preview';

            if (userMode === 'creative') {
                // --- CREATIVE MODE (DYNAMIC MODEL SELECTION) ---
                console.log(`[AI] Triggering ${userModel} Creative Rendering...`);

                const ext = initialResult.imageUrl.split('.').pop() || 'png';
                const mimeType = ext === 'gif' ? 'image/gif' : 'image/png';

                const model = genAI.getGenerativeModel({ model: userModel });

                const result = await model.generateContent([
                    { inlineData: { data: imgBuffer.toString("base64"), mimeType: mimeType } },
                    `Enhance this sports banner based on: ${userPrompt}. Focus on lighting, background, and professional artistic quality.`
                ]);

                const response = result.response;
                const candidates = response.candidates;
                if (candidates && candidates[0].content.parts[0].inlineData) {
                    const base64Img = candidates[0].content.parts[0].inlineData.data;
                    const buffer = Buffer.from(base64Img, 'base64');

                    const filename = `refined_creative_${size}_${Date.now()}.${ext}`;
                    const outputPath = path.join(__dirname, '..', 'backend', 'output', filename);
                    fs.writeFileSync(outputPath, buffer);

                    return res.json({
                        success: true,
                        imageUrl: `/output/${filename}`,
                        aiRefined: true,
                        info: `Creative AI Refinement Complete (Model: ${userModel})`
                    });
                }
            }
            else {
                // --- LAYOUT MODE (HYBRID JSON OVERRIDES) ---
                console.log("[AI] Triggering Layout Intent Mapping...");
                const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
                const systemPrompt = `Return JSON only. Analysis: banner coordinate overrides. Keys: title_y, player_1_scale, team_name_fs.`;

                const ext = initialResult.imageUrl.split('.').pop() || 'png';
                const mimeType = ext === 'gif' ? 'image/gif' : 'image/png';

                const result = await model.generateContent([
                    systemPrompt,
                    { inlineData: { data: imgBuffer.toString("base64"), mimeType: mimeType } },
                    `Intent: ${userPrompt}`
                ]);

                const aiText = result.response.text();
                console.log("[AI Suggestion]:", aiText);
                const jsonMatch = aiText.match(/\{.*\}/s);

                if (jsonMatch) {
                    const overrides = JSON.parse(jsonMatch[0]);
                    console.log("[AI] Applying Overrides to Python Engine:", overrides);
                    const refinedResult = await forwardToPython(overrides);

                    const ext = refinedResult.imageUrl.split('.').pop() || 'png';
                    const filename = `refined_layout_${size}_${Date.now()}.${ext}`;
                    const oldFilename = refinedResult.imageUrl.split('/').pop();
                    const oldPath = path.join(__dirname, '..', 'backend', 'output', oldFilename);
                    const newPath = path.join(__dirname, '..', 'backend', 'output', filename);

                    if (fs.existsSync(oldPath)) {
                        fs.renameSync(oldPath, newPath);
                        console.log(`[Flow] File Unique: ${filename}`);
                    }

                    return res.json({
                        success: true,
                        imageUrl: `/output/${filename}`,
                        aiRefined: true,
                        info: `Layout Refined (Hybrid): ${JSON.stringify(overrides)}`
                    });
                } else {
                    console.warn("[AI] No valid layout overrides found. Returning base.");
                    return res.json({ ...initialResult, info: "AI analyzed but suggested no layout changes." });
                }
            }
        } catch (aiErr) {
            console.error("[AI Logic Error]:", aiErr.message);
            return res.json({
                ...initialResult,
                error: `AI Error: ${aiErr.message}`,
                info: "Rolled back to base render due to AI timeout/error."
            });
        }

        res.json(initialResult);
    } catch (e) {
        console.error("[Fatal Error]:", e.message);
        res.status(500).json({ error: "System Error", detail: e.message });
    }
});

/**
 * Download Banner File
 */
app.get('/api/download/:filename', (req, res) => {
    const filename = req.params.filename;
    const filePath = path.join(__dirname, '..', 'backend', 'output', filename);

    if (fs.existsSync(filePath)) {
        res.download(filePath, filename);
    } else {
        res.status(404).send('File not found');
    }
});

app.listen(port, () => {
    console.log(`Agency Proxy running at http://localhost:${port}`);
    console.log(`V2.0 AI Multi-Mode Ready.`);
});

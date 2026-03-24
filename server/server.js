const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const sharp = require('sharp');

dotenv.config();

const app = express();
const port = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

const storage = multer.memoryStorage();
const upload = multer({
    storage: storage,
    limits: { fileSize: 10 * 1024 * 1024 }
});

// AI artık hangi ölçü için tasarım yaptığını biliyor
const extractDesignSpecs = async (userPrompt, width, height) => {
    const defaults = { glowColor: '#ffd000', accentColor: '#ffd000', atmosphere: 'sports stadium', layout: 'split', textColor: 'white' };
    if (!userPrompt) return defaults;

    const aspectRatio = width / height;
    const isVertical = aspectRatio < 0.8;

    try {
        const model = genAI.getGenerativeModel({ model: "nano-banana-pro-preview" });
        const result = await model.generateContent([
            `Analiz Et: "${userPrompt}"
             Hedef Ölçü: ${width}x${height} (Aspect Ratio: ${aspectRatio.toFixed(2)})
             
             Görev: Bu ölçüye ve konsepte uygun görsel tasarım parametrelerini belirle.
             JSON formatında dön: {"glowColor":hex, "accentColor":hex, "layout":"split"|"centered"|"vertical"}.
             Kural: Eğer alan darsa layout'u vertical yap.`
        ]);
        const jsonMatch = result.response.text().match(/\{.*\}/s);
        if (jsonMatch) return { ...defaults, ...JSON.parse(jsonMatch[0]) };
    } catch (e) {
        console.warn("[AI Spec Fail] Using defaults.");
    }
    return defaults;
};

app.post('/api/generate-asset', upload.fields([
    { name: 'logo1', maxCount: 1 }, { name: 'logo2', maxCount: 1 },
    { name: 'player1', maxCount: 1 }, { name: 'player2', maxCount: 1 },
    { name: 'bg', maxCount: 1 }
]), async (req, res) => {
    try {
        const { prompt, format, leagueData: leagueDataRaw } = req.body;
        const leagueData = typeof leagueDataRaw === 'string' ? JSON.parse(leagueDataRaw) : (leagueDataRaw || {});

        const isUEFA = leagueData.league && leagueData.league.toLowerCase().includes('uefa');
        const isZiraat = leagueData.league && leagueData.league.toLowerCase().includes('ziraat');

        console.log(`\n--- PRODUCTION: ${leagueData.league} ---`);

        const width = format === '1200' ? 1200 : (format === '120' ? 120 : (format === '320' ? 320 : 300));
        const height = format === '1200' ? 628 : (format === '120' ? 600 : (format === '320' ? 100 : 50));

        // Refined Asset Buffers with robust fallbacks
        const getB = (n) => {
            const p = path.join(__dirname, '..', 'public', 'assets', 'branding', n);
            return fs.existsSync(p) ? fs.readFileSync(p) : null;
        };

        const getAssetBuffer = async (fieldName, defaultFile, targetLeague) => {
            if (req.files && req.files[fieldName]) return req.files[fieldName][0].buffer;

            // Branding prioritisation based on league
            if (fieldName === 'logo1' || fieldName === 'logo2') {
                if (isUEFA) return getB('uefa_logo.png');
                if (isZiraat) return getB('ziraat_logo.png');
            }

            // General assets folder fallback
            const fallbackPath = path.join(__dirname, '..', 'assets', 'layers', defaultFile);
            if (fs.existsSync(fallbackPath)) return fs.readFileSync(fallbackPath);
            return null;
        };

        const designSpecs = await extractDesignSpecs(prompt, width, height);
        if (isUEFA) { designSpecs.bgBaseColor = '#000000'; designSpecs.glowColor = '#00ff00'; designSpecs.accentColor = '#00ff00'; }
        else if (isZiraat) { designSpecs.bgBaseColor = '#e8e8e8'; designSpecs.textColor = '#000000'; designSpecs.accentColor = '#cc0000'; }

        const brandBar = getB('nesine_brand_bar.png'); // Keep for old assets if needed
        const nesineLogo = getB('nesine_logo.png');
        const hemenOyna = getB('hemen_oyna.png');
        const leagueLogo = isUEFA ? getB('uefa_logo.png') : (isZiraat ? getB('ziraat_logo.png') : null);

        // ---------------------------------------------------------
        // 1200x628 BRANCH (Specific Refinement)
        // ---------------------------------------------------------
        if (width === 1200 && height === 628) {
            // 1. Background
            const bgB = await getAssetBuffer('bg', 'bg.png');
            let canvas;
            if (bgB) {
                canvas = sharp(bgB).resize(width, height, { fit: 'cover' });
            } else if (isZiraat) {
                canvas = sharp(Buffer.from(`<svg width="${width}" height="${height}"><rect width="100%" height="100%" fill="#e8e8e8"/><defs><pattern id="p" width="20" height="20" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="20" stroke="white" stroke-width="1"/></pattern></defs><rect width="100%" height="100%" fill="url(#p)"/></svg>`));
            } else {
                canvas = sharp({ create: { width, height, channels: 4, background: designSpecs.bgBaseColor || '#000' } });
            }

            const layers = [];

            // 2. Radial Glows
            if (isUEFA) {
                const uGlow = Buffer.from(`<svg width="${width}" height="${height}"><defs><radialGradient id="rg" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#00FF00" stop-opacity="0.5"/><stop offset="100%" stop-color="#00FF00" stop-opacity="0"/></radialGradient></defs><rect width="100%" height="100%" fill="url(#rg)"/></svg>`);
                layers.push({ input: uGlow, top: 0, left: 0 });
            } else if (isZiraat) {
                const leftGlow = Buffer.from(`<svg width="${width}" height="${height}"><defs><radialGradient id="lg" cx="20%" cy="50%" r="40%"><stop offset="0%" stop-color="#CC0000" stop-opacity="0.3"/><stop offset="100%" stop-color="#CC0000" stop-opacity="0"/></radialGradient></defs><rect width="100%" height="100%" fill="url(#lg)"/></svg>`);
                const rightGlow = Buffer.from(`<svg width="${width}" height="${height}"><defs><radialGradient id="rgn" cx="80%" cy="50%" r="40%"><stop offset="0%" stop-color="#003580" stop-opacity="0.3"/><stop offset="100%" stop-color="#003580" stop-opacity="0"/></radialGradient></defs><rect width="100%" height="100%" fill="url(#rgn)"/></svg>`);
                layers.push({ input: leftGlow, top: 0, left: 0 }, { input: rightGlow, top: 0, left: 0 });
            }

            // 3. Players
            const p1B = await getAssetBuffer('player1', 'player.png');
            const p2B = await getAssetBuffer('player2', 'player.png');
            const processP = async (b, right) => {
                if (!b) return null;
                let pH = height;
                let pWMax = Math.floor(width * 0.45);
                let img = sharp(b).resize({ height: pH, width: pWMax, fit: 'inside' });
                const res = await img.toBuffer();
                const m = await sharp(res).metadata();
                return { input: res, top: height - m.height, left: right ? width - m.width : 0 };
            };
            const p1 = await processP(p1B, false);
            const p2 = await processP(p2B, true);
            if (p1) layers.push(p1);
            if (p2) layers.push(p2);

            // 4. Team Logos
            const l1B = await getAssetBuffer('logo1', 'logo1.png');
            const l2B = await getAssetBuffer('logo2', 'logo2.png');
            const lS = Math.floor(width * 0.10);
            if (l1B) layers.push({ input: await sharp(l1B).resize({ width: lS, height: 120, fit: 'inside' }).toBuffer(), top: 40, left: 40 });
            if (l2B) layers.push({ input: await sharp(l2B).resize({ width: lS, height: 120, fit: 'inside' }).toBuffer(), top: 40, left: width - lS - 40 });

            // 5. League Logo & Branding
            if (leagueLogo) {
                const llW = 120;
                layers.push({ input: await sharp(leagueLogo).resize({ width: llW, height: 120, fit: 'inside' }).toBuffer(), top: 30, left: Math.floor(width / 2 - llW / 2) });
            }
            if (hemenOyna) {
                const hoW = 180;
                layers.push({ input: await sharp(hemenOyna).resize({ width: hoW, height: 80, fit: 'inside' }).toBuffer(), top: height - 120, left: Math.floor(width / 2 - hoW / 2) });
            }
            if (nesineLogo) {
                const nW = Math.floor(width * 0.12);
                layers.push({ input: await sharp(nesineLogo).resize({ width: nW, height: 60, fit: 'inside' }).toBuffer(), top: Math.floor(height - 60), left: Math.floor(width / 2 - nW / 2) });
            }

            // 6. Typography
            const team1 = leagueData.team1 || "TAKIM A";
            const team2 = leagueData.team2 || "TAKIM B";
            const svgT = Buffer.from(`<svg width="${width}" height="${height}">
                <style>
                    .z-t { fill: #000; font-family: sans-serif; font-size: 64px; font-weight: 900; text-transform: uppercase; letter-spacing: -1px; }
                    .z-i { fill: #444; font-family: sans-serif; font-size: 36px; font-weight: 700; letter-spacing: 1px; }
                </style>
                <text x="50%" y="${height / 2 - 40}" text-anchor="middle" class="z-t">${team1}</text>
                <text x="50%" y="${height / 2 + 30}" text-anchor="middle" class="z-t">${team2}</text>
                <text x="50%" y="${height / 2 + 80}" text-anchor="middle" class="z-i">${leagueData.day || 'PAZAR'} ${leagueData.hour || '20:30'}</text>
            </svg>`);
            layers.push({ input: svgT, top: 0, left: 0 });

            const final = await canvas.composite(layers).png().toBuffer();
            return res.json({ success: true, imageUrl: `data:image/png;base64,${final.toString('base64')}` });
        }

        // ---------------------------------------------------------
        // GENERIC BRANCH (Other sizes)
        // ---------------------------------------------------------
        const bgB = await getAssetBuffer('bg', 'bg.png');
        let canvas;
        if (bgB) {
            canvas = sharp(bgB).resize(width, height, { fit: 'cover' });
        } else if (isZiraat) {
            canvas = sharp(Buffer.from(`<svg width="${width}" height="${height}"><rect width="100%" height="100%" fill="#F2F2F2"/><defs><pattern id="p" width="15" height="15" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="15" stroke="#E0E0E0" stroke-width="1.5"/></pattern></defs><rect width="100%" height="100%" fill="url(#p)"/></svg>`));
        } else {
            canvas = sharp({ create: { width, height, channels: 4, background: designSpecs.bgBaseColor || '#000' } });
        }

        const layers = [];
        const isVertical = width < height || designSpecs.layout === 'vertical';
        const isCentered = !isVertical && designSpecs.layout === 'centered';

        // 2. UEFA Glow (Bottom Layer for Players)
        if (isUEFA) {
            const uGlow = Buffer.from(`<svg width="${width}" height="${height}"><defs><radialGradient id="rg" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#00FF00" stop-opacity="0.5"/><stop offset="100%" stop-color="#00FF00" stop-opacity="0"/></radialGradient></defs><rect width="100%" height="100%" fill="url(#rg)"/></svg>`);
            layers.push({ input: uGlow, top: 0, left: 0 });
        }

        // 4. Players
        const p1B = await getAssetBuffer('player1', 'player.png');
        const p2B = await getAssetBuffer('player2', 'player.png');
        const processP = async (b, right) => {
            if (!b) return null;
            let pH = isVertical ? Math.floor(height * 0.40) : Math.floor(height * 0.85);
            let pWMax = isVertical ? width : Math.floor(width * 0.9);
            let img = sharp(b).resize({ height: pH, width: pWMax, fit: 'inside' });
            const res = await img.toBuffer();
            const m = await sharp(res).metadata();

            let l = 0, t = 0;
            if (isVertical) {
                l = Math.floor(width / 2 - m.width / 2);
                t = right ? height - m.height - 20 : height - m.height * 1.5; // Stack vertically
            } else {
                l = right ? width - m.width - 5 : 5;
                t = height - m.height;
            }
            return { input: res, top: Math.floor(t), left: Math.floor(l) };
        };
        const p1 = await processP(p1B, false);
        const p2 = await processP(p2B, true);
        if (p1) layers.push(p1);
        if (p2) layers.push(p2);

        // 5. Logos
        const l1B = await getAssetBuffer('logo1', 'logo1.png');
        const l2B = await getAssetBuffer('logo2', 'logo2.png');
        const lS = isVertical ? Math.floor(width * 0.45) : Math.floor(width * 0.10);
        if (l1B) {
            const top = isVertical ? 20 : 40;
            const left = isVertical ? width / 2 - lS / 2 : (isCentered ? width / 2 - lS - 20 : 60);
            layers.push({ input: await sharp(l1B).resize({ width: lS, height: Math.floor(height * 0.2), fit: 'inside' }).toBuffer(), top: Math.floor(top), left: Math.floor(left) });
        }
        if (l2B && !isVertical) {
            const left = (isCentered ? width / 2 + 20 : width - lS - 60);
            layers.push({ input: await sharp(l2B).resize({ width: lS, height: Math.floor(height * 0.2), fit: 'inside' }).toBuffer(), top: 40, left: Math.floor(left) });
        }

        // 6. Branding & League Logo (Overlay)
        if (nesineLogo) {
            const nW = Math.floor(width * 0.12);
            layers.push({ input: await sharp(nesineLogo).resize({ width: nW, height: 60, fit: 'inside' }).toBuffer(), top: Math.floor(height - 80), left: Math.floor(width / 2 - nW / 2) });
        } else if (brandBar) {
            const bW = Math.floor(width * 0.30);
            layers.push({ input: await sharp(brandBar).resize({ width: bW, height: 80, fit: 'inside' }).toBuffer(), top: Math.floor(height - 100), left: Math.floor(width / 2 - bW / 2) });
        }

        if (leagueLogo) {
            const llW = Math.floor(width * 0.11);
            const llTop = Math.floor(height / 2 + 60);
            layers.push({ input: await sharp(leagueLogo).resize({ width: llW, height: Math.floor(height * 0.2), fit: 'inside' }).toBuffer(), top: Math.floor(llTop), left: Math.floor(width / 2 - llW / 2) });
        }

        // 6b. Hemen Oyna CTA
        if (hemenOyna) {
            const hoW = isVertical ? Math.floor(width * 0.7) : Math.floor(width * 0.18);
            const hoLeft = isVertical ? width / 2 - hoW / 2 : width - hoW - 20;
            const hoTop = isVertical ? height - 100 : height - 60;
            layers.push({ input: await sharp(hemenOyna).resize({ width: hoW, height: 80, fit: 'inside' }).toBuffer(), top: Math.floor(hoTop), left: Math.floor(hoLeft) });
        }

        // 7. Typography (Agency Quality - ON TOP)
        const team1 = leagueData.team1 || "TAKIM A";
        const team2 = leagueData.team2 || "TAKIM B";
        const title = leagueData.title || "MAÇ HEYECANI";

        const svgT = Buffer.from(`<svg width="${width}" height="${height}">
            <style>
                .u-h { fill: white; font-family: sans-serif; font-size: ${isVertical ? '18px' : '75px'}; font-weight: 900; filter: drop-shadow(0 0 20px rgba(0,255,0,0.4)); }
                .u-s { fill: #00ff00; font-family: sans-serif; font-size: ${isVertical ? '12px' : '40px'}; font-weight: 800; letter-spacing: 2px; }
            </style>
            ${isUEFA ? `
                <text x="50%" y="${isVertical ? height / 2 - 20 : 100}" text-anchor="middle" class="u-h">${title}</text>
                <text x="50%" y="${isVertical ? height / 2 + 10 : 220}" text-anchor="middle" class="u-s">${team1} v ${team2}</text>
            ` : `
                <text x="50%" y="${isVertical ? height / 2 : height - 150}" text-anchor="middle" font-size="${isVertical ? '14' : '55'}" font-weight="900" fill="white" font-family="sans-serif">${title}</text>
            `}
        </svg>`);
        layers.push({ input: svgT, top: 0, left: 0 });

        const final = await canvas.composite(layers).png().toBuffer();
        res.json({ success: true, imageUrl: `data:image/png;base64,${final.toString('base64')}` });

    } catch (e) {
        console.error(e);
        res.status(500).json({ success: false, error: e.message });
    }
});

// New Endpoint for Interactive HTML/CSS Content
app.post('/api/generate-interactive', upload.fields([
    { name: 'logo1', maxCount: 1 }, { name: 'logo2', maxCount: 1 },
    { name: 'player1', maxCount: 1 }, { name: 'player2', maxCount: 1 },
    { name: 'bg', maxCount: 1 }
]), async (req, res) => {
    try {
        const { prompt: userPrompt, format, leagueData: leagueDataRaw } = req.body;
        const leagueData = typeof leagueDataRaw === 'string' ? JSON.parse(leagueDataRaw) : (leagueDataRaw || {});

        const isUEFA = leagueData.league && leagueData.league.toLowerCase().includes('uefa');
        const isZiraat = leagueData.league && leagueData.league.toLowerCase().includes('ziraat');

        const width = format === '1200' ? 1200 : (format === '120' ? 120 : (format === '320' ? 320 : 300));
        const height = format === '1200' ? 628 : (format === '120' ? 600 : (format === '320' ? 100 : 50));

        const model = genAI.getGenerativeModel({ model: "nano-banana-pro-preview" });

        const systemPrompt = `
        Sen bir banner tasarımcısı ve frontend geliştiricisin. 
        Görevin: ${leagueData.league} ligi temasına uygun, ${width}x${height} ölçülerinde interaktif bir HTML/CSS banner oluşturmak.
        
        Kullanıcı Talebi: ${userPrompt}
        Takımlar: ${leagueData.team1} vs ${leagueData.team2}
        Başlık: ${leagueData.title}
        
        Teknik Kurallar:
        1. Çıktı tek bir HTML dosyası olmalı (içinde <style> ve gerekirse <script> barındıran).
        2. Tasarım modern, premium ve dinamik olmalı (hover efektleri, mikro animasyonlar).
        3. Dışardan resim linki verme, sadece renkler, gradientler ve CSS şekilleri kullan.
        4. Nesine.com renklerini (#ffd000, #000) ve ${isUEFA ? 'UEFA yeşili' : 'Ziraat kırmızısı'} tonlarını kullan.
        5. Font olarak sans-serif kullan.
        6. Metinler okunaklı ve hiyerarşik olmalı.
        7. Sadece ham HTML kodunu dön, markdown bloğu (backtick) kullanma.
        `;

        let cleanedHtml = "";
        try {
            const result = await model.generateContent(systemPrompt);
            cleanedHtml = result.response.text().replace(/```html|```/g, '').trim();
        } catch (aiError) {
            console.warn("AI Generation failed, using premium fallback:", aiError.message);
            cleanedHtml = `
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { margin: 0; font-family: sans-serif; overflow: hidden; background: #000; color: white; }
                    .banner { 
                        width: ${width}px; height: ${height}px; position: relative; overflow: hidden;
                        display: flex; flex-direction: column; justify-content: center; align-items: center;
                        background: ${isUEFA ? 'linear-gradient(135deg, #001a00, #000)' : 'linear-gradient(135deg, #1a0000, #000)'};
                        border: 1px solid rgba(255,208,0,0.3); box-sizing: border-box; transition: all 0.5s;
                    }
                    .banner:hover { border-color: #ffd000; }
                    .glow { position: absolute; top:0; left:0; width:100%; height:100%; 
                             background: radial-gradient(circle at 50% 50%, ${isUEFA ? 'rgba(0,255,0,0.2)' : 'rgba(255,0,0,0.15)'}, transparent 70%); }
                    .content { position: relative; z-index: 10; text-align: center; }
                    .title { font-size: ${height * 0.12}px; font-weight: 900; color: #ffd000; text-transform: uppercase; margin-bottom: 5px; }
                    .match { font-size: ${height * 0.15}px; font-weight: 700; margin: 10px 0; }
                    .cta { background: #ffd000; color: #000; padding: 5px 20px; font-weight: 900; border-radius: 4px; font-size: ${height * 0.08}px; box-shadow: 0 4px 15px rgba(255,208,0,0.3); }
                </style>
            </head>
            <body>
                <div class="banner">
                    <div class="glow"></div>
                    <div class="content">
                        <div class="title">${leagueData.title || (isUEFA ? 'AVRUPA HEYECANI' : 'TÜRKİYE KUPASI')}</div>
                        <div class="match">${leagueData.team1 || 'TEAM A'} VS ${leagueData.team2 || 'TEAM B'}</div>
                        <div class="cta">HEMEN OYNA</div>
                    </div>
                </div>
            </body>
            </html>`;
        }

        res.json({ success: true, html: cleanedHtml });

    } catch (e) {
        console.error(e);
        res.status(500).json({ success: false, error: e.message });
    }
});

app.listen(port, () => console.log(`Agency Backend running on ${port}`));

const { GoogleGenerativeAI } = require('@google/generative-ai');
const dotenv = require('dotenv');
dotenv.config();

async function list() {
    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
    try {
        // Attempt to call the listModels endpoint
        // In @google/generative-ai, this might not be exposed directly in all versions 
        // but we can try common ones like 'v1'
        console.log("Checking v1 models...");
        // Actually, the easiest way to find out what's wrong is to check 
        // if ANY model works.
        const models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro", "gemini-1.0-pro"];
        for (const m of models) {
            try {
                const model = genAI.getGenerativeModel({ model: m }, { apiVersion: 'v1' });
                const result = await model.generateContent("test");
                console.log(`v1 Model ${m} works!`);
                return;
            } catch (e) {
                console.log(`v1 Model ${m} failed: ${e.message}`);
            }
        }
    } catch (e) {
        console.error("List failed:", e.message);
    }
}
list();

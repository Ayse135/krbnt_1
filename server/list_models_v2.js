const { GoogleGenerativeAI } = require('@google/generative-ai');
const dotenv = require('dotenv');
dotenv.config();

async function list() {
    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
    try {
        // Try to list models using the correct method if available in this SDK version
        // Some versions use genAI.listModels()
        console.log("Attempting to list models...");
        // This is a bit of a hack but let's see if we can get anything
        const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
        const result = await model.generateContent("test");
        console.log("gemini-1.5-flash works!");
    } catch (e) {
        console.log("gemini-1.5-flash failed:", e.message);
        try {
            const model = genAI.getGenerativeModel({ model: "gemini-pro" });
            const result = await model.generateContent("test");
            console.log("gemini-pro works!");
        } catch (e2) {
            console.log("gemini-pro failed:", e2.message);
        }
    }
}
list();

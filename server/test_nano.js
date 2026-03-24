const { GoogleGenerativeAI } = require('@google/generative-ai');
const dotenv = require('dotenv');
dotenv.config();

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

async function test() {
    try {
        const model = genAI.getGenerativeModel({ model: "nano-banana-pro-preview" });
        const result = await model.generateContent("Hello! Are you ready to design some sports banners?");
        console.log("Success! Nano-Banana-Pro response:", result.response.text());
    } catch (e) {
        console.error("Nano-Banana-Pro failed:", e.message);
    }
}
test();

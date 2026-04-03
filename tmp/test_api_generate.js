async function testGenerate() {
    console.log("Testing API Generation (/api/generate-asset) using native fetch...");
    try {
        const response = await fetch('http://localhost:3001/api/generate-asset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: "UEFA match with gold highlights",
                format: "1200",
                leagueData: JSON.stringify({
                    league: "UEFA Champions League",
                    team1: "Real Madrid",
                    team2: "Manchester City",
                    day: "Çarşamba",
                    hour: "22:00",
                    title: "DEV MAÇ"
                })
            })
        });

        const data = await response.json();
        if (data.success) {
            console.log("✅ API Success!");
            console.log("Image URL (Preview):", data.imageUrl.substring(0, 50) + "...");
            console.log("Response size:", data.imageUrl.length, "bytes");
        } else {
            console.log("❌ API Fail:", data.error);
        }
    } catch (error) {
        console.error("❌ Request Error:", error.message);
    }
}

testGenerate();

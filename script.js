document.getElementById("generateBtn").addEventListener("click", async () => {
    const occasion = document.getElementById("occasionInput").value;
    const gender = document.getElementById("genderInput").value;

    const btn = document.getElementById("generateBtn");
    const suggestionEl = document.getElementById("suggestion");
    const audioEl = document.getElementById("audio");
    const carousel = document.getElementById("carousel");

    btn.disabled = true;
    btn.textContent = "Generating...";

    try {
        const response = await fetch("/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ occasion, gender })
        });

        const data = await response.json();

        if (data.error) {
            suggestionEl.textContent = data.error;
            audioEl.src = "";
        } else {
            suggestionEl.textContent = data.suggestion;
            audioEl.src = data.audio;
            audioEl.load();
            audioEl.play();

            if (data.image) {
                const img = document.createElement("img");
                img.src = data.image;
                carousel.appendChild(img);
                img.scrollIntoView({ behavior: "smooth", inline: "center" });
            }
        }
    } catch (err) {
        suggestionEl.textContent = "Something went wrong. Try again!";
        audioEl.src = "";
        console.error(err);
    } finally {
        btn.disabled = false;
        btn.textContent = "Generate Outfit";
    }
});

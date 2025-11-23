console.log("script.js loaded");

document.addEventListener("DOMContentLoaded", () => {
    const searchBtn = document.querySelector(".search");

    searchBtn.addEventListener("click", (e) => {
        e.preventDefault();

        const query = document.getElementById("query").value.trim();

        if (!query) {
            alert("Please enter a search query");
            return;
        }

        console.log("Sending POST request with query:", query);

        fetch("http://127.0.0.1:5000/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        })
        .then(res => res.json())
        .then(data => {
            console.log("Server response:", data);
            showResults(data.results || []);
        })
        .catch(err => {
            console.error("Error:", err);
            alert("Search failed — check console.");
        });
    });
});

// DISPLAY SEARCH RESULTS
function showResults(results) {
    let container = document.getElementById("results");

    if (!container) {
        container = document.createElement("div");
        container.id = "results";
        container.style.width = "90%";
        container.style.maxWidth = "800px";
        container.style.margin = "30px auto";
        document.body.appendChild(container);
    }

    container.innerHTML = "";

    if (results.length === 0) {
        container.innerHTML = "<p>No results found</p>";
        return;
    }

    results.forEach(item => {
        const card = document.createElement("div");

        card.style.cssText = `
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 25px;
            background: white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            align-items: center;
        `;

        card.innerHTML = `
        <div style="
            position: relative;
            width: 100%;
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;
            border-radius: 10px;
        ">
            <iframe 
                src="https://www.youtube.com/embed/${item.id}"
                frameborder="0"
                allowfullscreen
                style="
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    border-radius: 10px;
                ">
            </iframe>
        </div>
        
        <div style="
            display:flex;
            justify-content:space-between;
            width:100%;
            margin-top:10px;
            padding: 0 10px;
            font-size:1.1em;
        ">
            <span><strong>Views:</strong> ${item.viewCount}</span>
            <span><strong>Likes:</strong> ${item.likeCount}</span>
        </div>

        <strong style="
            margin-top:15px;
            font-size:1.3em;
            text-align:center;
            padding:2px;
        ">
            ${item.title.replace(/\b\w/g, c => c.toUpperCase())}
        </strong>

        <p style="font-size:1.2em; text-align:center; padding:2px;">
            <strong>Channel:</strong> 
            ${item.channel_title.replace(/\b\w/g, c => c.toUpperCase())}
        </p>

        <p style="font-size:1.1em; padding:2px;">
            <strong>Similarity Score:</strong> ${item.score.toFixed(3)}
        </p>

        <button class="summarize-btn"
            data-id="${item.id}"
            style="
                margin-top:10px;
                padding:12px 20px;
                background:#007bff;
                color:white;
                border:none;
                font-size:16px;
                border-radius:8px;
                cursor:pointer;
                transition: 0.2s ease;
            ">
            Summarize
        </button>

        <!-- SUMMARY BOX WITH CLOSE BUTTON -->
        <div id="summary-${item.id}"
            style="
                display:none;
                margin-top:15px;
                font-size:15px;
                line-height:22px;
                padding:50px 20px 20px 20px;
                border:1px solid #ddd;
                border-radius:8px;
                background:#f9f9f9;
                position:relative;
                text-align:justify;
        ">
            
        <span class="close-summary" 
               data-id="${item.id}"
               style="
                   position:absolute;
                   top:5px;
                   right:5px;
                   cursor:pointer;
                   font-size:24px;
                   color:#333;
                   font-weight:bold;
                   padding:8px 12px;
                   background:white;
                   border-radius:8px;
                   box-shadow:0 2px 6px rgba(0,0,0,0.25);
                   z-index:10;
               "
               onmouseover="this.style.background='#c92222ff'; this.style.color='white'"
                onmouseout="this.style.background='white'; this.style.color='black'"
                >
               &times;
        </span>    


            <div class="summary-text"></div>
        </div>
        `;

        container.appendChild(card);
    });

    attachSummaryHandlers();
}


// SUMMARY HANDLER 
function attachSummaryHandlers() {

    // Summarize Button
    document.querySelectorAll(".summarize-btn").forEach(btn => {
        btn.addEventListener("click", async () => {

            const videoID = btn.dataset.id;
            const summaryBox = document.getElementById(`summary-${videoID}`);
            const textBox = summaryBox.querySelector(".summary-text");

            summaryBox.style.display = "block";
            textBox.innerHTML = "<b>Generating summary...</b>";

            try {
                let response = await fetch("http://127.0.0.1:5000/generate_summary", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ video_id: videoID })
                });

                let data = await response.json();

                if (data.summary) {
                    textBox.innerHTML = data.summary.replace(/\n/g, "<br>");
                } else {
                    textBox.innerHTML = `<span style="color:red;">${data.error}</span>`;
                }

            } catch (err) {
                textBox.innerHTML = `<span style="color:red;"><b>Error:</b> ${err}</span>`;
            }
        });
    });

    // Close Button
    document.querySelectorAll(".close-summary").forEach(closeBtn => {
        closeBtn.addEventListener("click", () => {
            const id = closeBtn.dataset.id;
            document.getElementById(`summary-${id}`).style.display = "none";
        });
    });
}

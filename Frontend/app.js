
// ==================================================
// BACKEND URL
// ==================================================

const API_URL = "http://127.0.0.1:8000";


// ==================================================
// ELEMENTS
// ==================================================

const fileInput = document.getElementById("fileInput");
const dropZone = document.getElementById("dropZone");
const selectedFiles = document.getElementById("selectedFiles");


// ==================================================
// FILE SELECTION
// ==================================================

fileInput.addEventListener("change", function () {
    displaySelectedFiles(fileInput.files);
});


// ==================================================
// DRAG AND DROP
// ==================================================

dropZone.addEventListener("dragover", function (event) {
    event.preventDefault();
    dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", function () {
    dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", function (event) {
    event.preventDefault();
    dropZone.classList.remove("dragover");

    const files = event.dataTransfer.files;
    fileInput.files = files;

    displaySelectedFiles(files);
});


// ==================================================
// DISPLAY SELECTED FILES
// ==================================================

function displaySelectedFiles(files) {
    selectedFiles.innerHTML = "";

    if (!files || files.length === 0) {
        return;
    }

    Array.from(files).forEach(function (file) {
        const div = document.createElement("div");
        div.className = "file-chip";

        const extension = file.name
            .split(".")
            .pop()
            .toUpperCase();

        let icon = "📄";

        if (extension === "PDF") {
            icon = "PDF";
        } else if (extension === "DOCX") {
            icon = "DOC";
        } else if (extension === "TXT") {
            icon = "TXT";
        }

        div.innerHTML = `
            <div class="file-type">
                ${icon}
            </div>

            <div>
                ${escapeHTML(file.name)}
            </div>
        `;

        selectedFiles.appendChild(div);
    });
}


// ==================================================
// PROCESS DOCUMENTS
// ==================================================

async function processDocuments() {
    const files = fileInput.files;

    const status = document.getElementById("processStatus");
    const processing = document.getElementById("processingStatus");

    if (!files || files.length === 0) {
        status.innerText = "Please select at least one document.";
        status.style.color = "#dc2626";
        return;
    }

    const formData = new FormData();

    for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
    }

    status.innerText =
        "⏳ Extracting text, creating embeddings and building FAISS index...";

    status.style.color = "#4f46e5";
    processing.innerText = "Processing";

    try {
        const response = await fetch(`${API_URL}/process`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Processing failed.");
        }

        status.innerText =
            `✓ ${data.documents} documents processed · ${data.chunks} chunks created`;

        status.style.color = "#16a34a";
        processing.innerText = "Complete";

        updateStats(data.documents, data.chunks);

        await loadDocuments();

    } catch (error) {
        status.innerText = "✕ " + error.message;
        status.style.color = "#dc2626";
        processing.innerText = "Error";
    }
}


// ==================================================
// LOAD DOCUMENTS
// ==================================================

async function loadDocuments() {
    const container = document.getElementById("documentInfo");

    try {
        const response = await fetch(`${API_URL}/documents`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Could not load documents.");
        }

        if (!data.documents || data.documents.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div>▤</div>

                    <p>
                        No documents processed yet.
                    </p>

                    <span>
                        Upload documents above to begin.
                    </span>
                </div>
            `;

            updateStats(0, 0);
            return;
        }

        container.innerHTML = "";

        // Corrected: use doc instead of document
        data.documents.forEach(function (doc) {
            const card = document.createElement("div");

            card.className = "document-card";

            const extension = doc.name
                .split(".")
                .pop()
                .toUpperCase();

            card.innerHTML = `
                <div class="doc-top">

                    <div class="doc-icon">
                        📄
                    </div>

                    <div class="doc-name">
                        ${escapeHTML(doc.name)}
                    </div>

                </div>

                <div class="doc-info">

                    <span>
                        ${doc.words} words
                    </span>

                    <span>
                        ${doc.chunks} chunks
                    </span>

                    <span>
                        ${extension}
                    </span>

                </div>
            `;

            container.appendChild(card);
        });

        let totalChunks = 0;

        data.documents.forEach(function (doc) {
            totalChunks += doc.chunks;
        });

        updateStats(
            data.documents.length,
            totalChunks
        );

    } catch (error) {
        console.error(
            "Document loading error:",
            error
        );
    }
}


// ==================================================
// UPDATE STATS
// ==================================================

function updateStats(documents, chunks) {
    document.getElementById("documentCount").innerText = documents;

    document.getElementById("chunkCount").innerText = chunks;
}


// ==================================================
// GENERATE SUMMARY
// ==================================================


async function generateSummary() {
    const summary = document.getElementById("summary");
    summary.replaceChildren();

    const status = document.createElement("p");
    status.className = "summary-status";
    status.textContent = "Preparing summary...";
    summary.appendChild(status);

    const sections = [
        ["overall", "Overall Summary"],
        ["topics", "Main Topics"],
        ["important", "Important Points"],
        ["common", "Common Information"],
        ["differences", "Differences Between Documents"],
        ["conclusion", "Final Conclusion"]
    ];

    const sectionElements = {};

    sections.forEach(([id, title]) => {
        const card = document.createElement("div");
        card.className = "summary-content";

        const heading = document.createElement("h3");
        heading.textContent = title;

        const sectionStatus = document.createElement("p");
        sectionStatus.textContent = "Waiting";

        const content = document.createElement("div");
        content.style.whiteSpace = "pre-wrap";

        card.append(heading, sectionStatus, content);
        summary.appendChild(card);

        sectionElements[id] = { sectionStatus, content };
    });

    try {
        const response = await fetch(`${API_URL}/summarize`, {
            method: "POST"
        });

        if (!response.ok) {
            let message = "Summary generation failed.";

            try {
                const data = await response.json();
                message = data.detail || message;
            } catch (_) {}

            throw new Error(message);
        }

        if (!response.body) {
            throw new Error("Streaming is not supported by this browser.");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        function handleEvent(event) {
            if (event.type === "status") {
    status.textContent = "⏳ " + event.message;

    // Keep the progress message visible.
    status.style.color = "#4f46e5";
}

            if (event.type === "section_start") {
                const section = sectionElements[event.id];

                if (section) {
                    section.sectionStatus.textContent = "Generating...";
                    section.content.textContent = "";
                    status.textContent = event.message;
                }
            }

            if (event.type === "token") {
                const section = sectionElements[event.id];

                if (section) {
                    section.content.textContent += event.text;
                }
            }

            if (event.type === "section_complete") {
                const section = sectionElements[event.id];

                if (section) {
                    section.sectionStatus.textContent = "Complete";
                }
            }

            if (event.type === "complete") {
                status.textContent = event.message;
            }

            if (event.type === "error") {
                throw new Error(event.message);
            }
        }

        while (true) {
            const { value, done } = await reader.read();

            buffer += decoder.decode(value || new Uint8Array(), {
                stream: !done
            });

            const lines = buffer.split("\n");
            buffer = lines.pop() || "";

            for (const line of lines) {
                if (line.trim()) {
                    handleEvent(JSON.parse(line));
                }
            }

            if (done) break;
        }

        if (buffer.trim()) {
            handleEvent(JSON.parse(buffer));
        }

    } catch (error) {
        status.textContent = "Error: " + error.message;
    }
}



// ==================================================
// ASK QUESTION
// ==================================================


async function askQuestion() {
    const input = document.getElementById("questionInput");
    const answer = document.getElementById("answer");

    const question = input.value.trim();

    if (!question) {
        answer.innerHTML = `
            <div class="answer-placeholder">
                <h3>Please enter a question</h3>
                <p>Ask something about your uploaded documents.</p>
            </div>
        `;
        return;
    }

    // Create the answer area immediately
    answer.innerHTML = `
        <div class="answer-content">
            <strong>Generating answer...</strong>
            <div id="streamedAnswer"
                 style="white-space: pre-wrap; margin-top: 10px;"></div>
            <div id="answerStatus">Retrieving relevant passages...</div>
        </div>
        <div id="answerSources"></div>
    `;

    const answerText = document.getElementById("streamedAnswer");
    const answerStatus = document.getElementById("answerStatus");
    const sourcesContainer = document.getElementById("answerSources");

    try {
        const response = await fetch(`${API_URL}/ask`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question })
        });

        if (!response.ok) {
            let message = "Question answering failed.";

            try {
                const errorData = await response.json();
                message = errorData.detail || message;
            } catch (_) {}

            throw new Error(message);
        }

        if (!response.body) {
            throw new Error("Streaming is not supported by this browser.");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        function handleEvent(event) {
            if (event.type === "token") {
                // Append text immediately as each token arrives
                answerText.textContent += event.text;
                answerStatus.textContent = "Generating answer...";
            }

            if (event.type === "complete") {
                answerStatus.textContent = "Answer complete.";
            }

            if (event.type === "error") {
                throw new Error(event.message);
            }

            // Optional: display sources if the backend sends them
            if (event.type === "sources" &&
                Array.isArray(event.sources)) {

                let sourcesHTML = `
                    <div class="sources">
                        <div class="sources-title">Retrieved Sources</div>
                `;

                event.sources.forEach(function (source, index) {
                    const score =
                        source.score !== undefined &&
                        source.score !== null
                            ? Number(source.score).toFixed(3)
                            : "N/A";

                    sourcesHTML += `
                        <div class="source">
                            <strong>
                                ${index + 1}.
                                ${escapeHTML(
                                    source.document || "Unknown document"
                                )}
                            </strong>
                            <br>
                            Similarity: ${score}
                        </div>
                    `;
                });

                sourcesHTML += "</div>";
                sourcesContainer.innerHTML = sourcesHTML;
            }
        }

        while (true) {
            const { value, done } = await reader.read();

            buffer += decoder.decode(
                value || new Uint8Array(),
                { stream: !done }
            );

            const lines = buffer.split("\n");
            buffer = lines.pop() || "";

            for (const line of lines) {
                if (line.trim()) {
                    handleEvent(JSON.parse(line));
                }
            }

            if (done) break;
        }

        // Handle a final event if the stream ends without a newline
        if (buffer.trim()) {
            handleEvent(JSON.parse(buffer));
        }

        if (!answerText.textContent.trim()) {
            answerText.textContent = "No answer was returned.";
        }

    } catch (error) {
        answerStatus.textContent = "Error: " + error.message;
    }
}




// ==================================================
// ENTER KEY FOR QUESTION
// ==================================================

document.getElementById("questionInput").addEventListener(
    "keydown",
    function (event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            askQuestion();
        }
    }
);


// ==================================================
// HTML ESCAPE
// ==================================================

function escapeHTML(text) {
    const div = document.createElement("div");

    div.textContent = text ?? "";

    return div.innerHTML;
}

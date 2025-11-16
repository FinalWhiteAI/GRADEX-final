

import React, { useState, useEffect } from "react";

// --- CONFIGURATION ---
const USER_ID = "734efeb8-6a3c-44f3-b949-490602e986e7";
const API_BASE_URL = "https://760eacb1e388.ngrok-free.app";
const API_BASE_URL_2 = "https://k5flk5h4-8000.inc1.devtunnels.ms/";

// -----------------------------------------------------------------
// 1. CHAT INTERFACE COMPONENT
// -----------------------------------------------------------------
const ChatInterface = ({ docName, messages, isLoading, onSendMessage }) => {
  const [input, setInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input);
    setInput("");
  };

  return (
    <div className="flex flex-col h-full">
      <div className="border-b border-white/20 pb-2 mb-4">
        <h2 className="text-xl font-bold">Chat with: {docName}</h2>
      </div>

      <div className="flex-1 overflow-y-auto pr-2">
        <div className="flex flex-col gap-4">
          {messages.map((msg, index) => (
            <div key={index} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[70%] p-3 rounded-xl ${
                  msg.sender === "user" ? "bg-blue-600 text-white" : "bg-gray-700 text-white"
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
          {isLoading && messages.length === 0 && (
            <div className="text-gray-400 text-center animate-pulse">
              Starting chat session...
            </div>
          )}
        </div>
      </div>

      <div className="mt-4 flex gap-4 fixed bottom-1 w-1/2 left-1/2 transform -translate-x-1/2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit(e)}
          placeholder="Ask a question about the document..."
          className="flex-1 p-3 rounded-lg bg-gray-800 border border-gray-700 text-white"
          disabled={isLoading}
        />
        <button
          onClick={handleSubmit}
          className="px-3 py-4 bg-blue-600 rounded-lg text-white font-semibold hover:bg-blue-700 disabled:bg-gray-600"
          disabled={isLoading || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
};

// -----------------------------------------------------------------
// 2. CODE EDITOR COMPONENT
// -----------------------------------------------------------------
const CodeEditor = ({ code, setCode, onRun }) => {
  return (
    <div className="flex flex-col h-full">
      <div className="border-b border-white/20 pb-2 mb-4">
        <h2 className="text-xl font-bold">Code Editor</h2>
      </div>

      <div className="flex-1 bg-gray-800 rounded-lg p-4">
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          className="w-full h-full bg-transparent text-white font-mono resize-none border-none outline-none"
          placeholder="Write your code here..."
        />
      </div>

      <div className="mt-4 flex justify-end">
        <button
          onClick={onRun}
          className="px-5 py-2 bg-green-600 rounded-lg text-white font-semibold hover:bg-green-700"
        >
          Run Code
        </button>
      </div>
    </div>
  );
};


// -----------------------------------------------------------------
// 3. MAIN APP COMPONENT
// -----------------------------------------------------------------
export default function App() {
  const [documentId, setDocumentId] = useState(null);
  const [docHistory, setDocHistory] = useState([]);
  const [isUploading, setIsUploading] = useState(false);

  const [chatSessionId, setChatSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoadingChat, setIsLoadingChat] = useState(false);
  const [currentChatDocName, setCurrentChatDocName] = useState("");

  const [activeView, setActiveView] = useState("chat");

  const [searchNotes, setSearchNotes] = useState([]);
  const [isLoadingNotes, setIsLoadingNotes] = useState(false);
  const [showNotesDropdown, setShowNotesDropdown] = useState(false);




  const [code, setCode] = useState("");
  const [output, setOutput] = useState(null);

  // ---------------- FETCH DOCUMENTS ----------------
  const fetchDocuments = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/documents/${USER_ID}`, {
        method: "GET",
        headers: { "ngrok-skip-browser-warning": "true" },
      });

      if (response.ok) {
        const data = await response.json();
        const docs = (data.documents || []).map((d) => ({
          id: d.document_id,
          name: d.file_name,
        }));
        setDocHistory(docs);
      } else {
        setDocHistory([]);
      }
    } catch (error) {
      console.error("Error connecting to backend:", error);
      setDocHistory([]);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  // ---------------- FILE UPLOAD ----------------
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      setIsUploading(true);
      const formData = new FormData();
      formData.append("file", file);
      formData.append("user_id", USER_ID);

      const response = await fetch(`${API_BASE_URL}/upload/`, {
        method: "POST",
        body: formData,
        headers: { "ngrok-skip-browser-warning": "true" },
      });

      if (response.ok) {
        await fetchDocuments();
      } else {
        alert("Upload failed");
      }
    } catch (error) {
      console.error(error);
      alert("Upload failed");
    } finally {
      setIsUploading(false);
      e.target.value = null;
    }
  };


  // ---------------- RUN CODE ----------------
  const runCode = async () => {
  if (!code.trim()) return;

  try {
    const response = await fetch("https://wqlq1078-8000.inc1.devtunnels.ms/execute", {
      method: "POST",
      headers: { "Content-Type": "text/plain" },
      body: code,
    });

    const data = await response.json();
    setOutput(data); // update output panel
  } catch (err) {
    setOutput({
      stdout: "",
      stderr: "Error connecting to backend",
      exit_code: -1
    });
  }
};


  // ---------------- FETCH NOTES (FIREBASE FASTAPI) ----------------
  const handleSearchNotes = async () => {
    try {
      setIsLoadingNotes(true);
      setShowNotesDropdown(false);

      const response = await fetch(`${API_BASE_URL_2}api/user/${USER_ID}/section/notes`);

      if (!response.ok) {
        alert("Failed to fetch notes");
        return;
      }

      const data = await response.json();
      const notesArray = Array.isArray(data) ? data : data.notes || [];

      const notes = notesArray.map((note) => ({
        id: note.id || note.note_id,
        title: note.title || note.name,
        file_path: note.file_url,
      }));
      console.log("Fetched notes:", notes);
      setSearchNotes(notes);
      setShowNotesDropdown(true);
    } catch (error) {
      alert("Error fetching notes");
    } finally {
      setIsLoadingNotes(false);
    }
  };

  // ---------------- HANDLE NOTE SELECTION ----------------
  const handleNoteSelect = async (note) => {
    try {
      if (!note || !note.file_path) {
    console.error("Selected note is missing a 'file_path':", note);
    alert(
      "Error: This note does not have an associated file path and cannot be processed.",
    );
    setShowNotesDropdown(false); // Still close the dropdown
    return; // Stop execution
  }
      const response = await fetch(`${API_BASE_URL}/upload-from-url/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: USER_ID,
          file_url: note.file_path,
        }),
      });

      if (!response.ok) {
        alert("Upload from URL failed");
        return;
      }

      const data = await response.json();

      const newDoc = {
        id: data.document_id,
        name: data.file_name || note.title,
      };

      setDocHistory((prev) => [...prev, newDoc]);

      handleDocumentSelect(newDoc.id, newDoc.name);
    } catch (error) {
      alert("Error connecting to upload-from-url");
    }

    setShowNotesDropdown(false);
  };

  // ---------------- SELECT DOCUMENT (OPEN CHAT) ----------------
  const handleDocumentSelect = (id, name) => {
    setDocumentId(id);
    setCurrentChatDocName(name);
    setMessages([
      { sender: "bot", text: `Chat started for ${name}. Ask anything!` },
    ]);
    setChatSessionId(crypto.randomUUID());
  };

  // ---------------- SEND RAG QUERY ----------------
  const handleSendMessage = async (userText) => {
    const newMessages = [...messages, { sender: "user", text: userText }];
    setMessages(newMessages);
    setIsLoadingChat(true);

    try {
      const response = await fetch(`${API_BASE_URL}/query/rag/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "ngrok-skip-browser-warning": "true",
        },
        body: JSON.stringify({
          user_id: USER_ID,
          document_id: documentId,
          query: userText,
          chat_session_id: chatSessionId,
        }),
      });

      const data = await response.json();
      const botText = data.answer || "No answer returned";

      setMessages([...newMessages, { sender: "bot", text: botText }]);
    } catch (error) {
      setMessages([
        ...newMessages,
        { sender: "bot", text: "Error contacting backend" },
      ]);
    }

    setIsLoadingChat(false);
  };

  // -----------------------------------------------------------------
  // UI
  // -----------------------------------------------------------------
  return (
    <div className="grid grid-cols-12 gap-4 p-4 h-screen bg-gray-900 text-white">
      {/* LEFT SIDEBAR */}
      <div className="col-span-3 flex flex-col gap-4">
        {/* Upload */}
        <div className="p-4 bg-white/10 rounded-xl">
          <h2 className="text-lg font-bold mb-3">Upload PDF</h2>
          <label className="flex justify-center items-center cursor-pointer px-4 py-2 bg-blue-600 rounded-lg">
            {isUploading ? "Uploading..." : "Select & Upload"}
            <input
              type="file"
              accept="application/pdf"
              className="hidden"
              disabled={isUploading}
              onChange={handleFileUpload}
            />
          </label>
        </div>

        {/* Load Firebase */}
        <div className="p-4 bg-white/10 rounded-xl">
          <button
            onClick={handleSearchNotes}
            className="w-full bg-green-600 p-2 rounded"
          >
            Fetch Documents
          </button>
        </div>

        {/* Notes Dropdown */}
        <div className="p-4 bg-white/10 rounded-xl relative">
          <button
            onClick={handleSearchNotes}
            disabled={isLoadingNotes}
            className="w-full bg-purple-600 p-2 rounded"
          >
            {isLoadingNotes ? "Loading..." : "Search Notes"}
          </button>

          {showNotesDropdown && searchNotes.length > 0 && (
            <div className="absolute left-0 right-0 mt-2 bg-gray-800 border text-white rounded-xl max-h-60 overflow-y-auto z-50">
              {searchNotes.map((note) => (
                <button
                  key={note.id}
                  onClick={() => handleNoteSelect(note)}
                  className="block w-full text-left px-4 py-2 hover:bg-gray-700"
                >
                  📝 {note.title}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Document History */}
        <div className="p-4 bg-white/10 rounded-xl flex-1 overflow-y-auto">
          <h2 className="text-xl font-bold mb-3">Document History</h2>

          {docHistory.map((doc) => (
            <button
              key={doc.id}
              onClick={() => handleDocumentSelect(doc.id, doc.name)}
              className={`block w-full text-left px-3 py-2 rounded ${
                doc.id === documentId ? "bg-blue-600" : "hover:bg-gray-700"
              }`}
            >
              📄 {doc.name}
            </button>
          ))}
        </div>
      </div>

      {/* CENTER SECTION */}
      <div className="col-span-6 p-4 bg-white/10 rounded-xl overflow-y-auto flex flex-col">
        <div className="flex border-b pb-2 mb-4">
          <button
            onClick={() => setActiveView("chat")}
            className={`mr-4 ${activeView === "chat" ? "text-white border-b-2 border-blue-500" : "text-gray-400"
              }`}
          >
            Chat Notebook
          </button>
          <button
            onClick={() => setActiveView("code")}
            className={`${activeView === "code" ? "text-white border-b-2 border-blue-500" : "text-gray-400"
              }`}
          >
            Code Editor
          </button>
        </div>

        <div className="h-full">
          {activeView === "chat" ? (
            !documentId ? (
              <div className="text-center text-gray-400 mt-20">
                Select a document to begin chat.
              </div>
            ) : (
              <ChatInterface
                docName={currentChatDocName}
                messages={messages}
                isLoading={isLoadingChat}
                onSendMessage={handleSendMessage}
              />
            )
          ) : (
            <CodeEditor code={code} setCode={setCode} onRun={runCode} />

          )}
        </div>
      </div>

      {/* RIGHT SECTION */}
      <div className="col-span-3 p-4 bg-white/10 rounded-xl">
  {activeView === "code" ? (
    <>
      <h2 className="text-xl font-bold mb-3">Output</h2>

      {output ? (
        <div className="bg-gray-800 p-3 rounded-lg text-sm whitespace-pre-wrap">
          <strong>STDOUT:</strong>
          <pre className="text-green-400">{output.stdout || " "}</pre>

          <strong>STDERR:</strong>
          <pre className="text-red-400">{output.stderr || " "}</pre>

          <strong>Exit Code:</strong> {output.exit_code}
        </div>
      ) : (
        <p className="text-gray-400">Run code to see output</p>
      )}
    </>
  ) : (
    <>
      <h2 className="text-xl font-bold mb-3">Analysis Panel</h2>
      {documentId ? (
        <div>
          <p>ID: {documentId}</p>
          <p>Session: {chatSessionId}</p>
        </div>
      ) : (
        <p>No document selected</p>
      )}
    </>
  )}
</div>

    </div>
  );
}

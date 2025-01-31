import React, { useState, useEffect } from "react";
import ChatWindow from "./ChatWindow";
import InputBar from "./InputBar";
import Header from "./Header";
import "./App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:5000";

function App() {
  const [messages, setMessages] = useState([]);
  const [isDataUploaded, setIsDataUploaded] = useState(false);
  const [showUploadPopup, setShowUploadPopup] = useState(false);
  const [isWaiting, setIsWaiting] = useState(true);

  useEffect(() => {
    const checkDatabase = async () => {
      setIsWaiting(true);
      try {
        const response = await fetch(`${BACKEND_URL}/check-database`);
        const data = await response.json();
        setIsDataUploaded(data.ready);

        if (!data.ready) {
          setMessages([
            {
              sender: "bot",
              text: "Welcome to the app! Please upload your Spotify data to get started.",
              showUploadButton: true,
            },
          ]);
        } else {
          setMessages([
            {
              sender: "bot",
              text: "Welcome back! You can now ask questions about your Spotify data.",
            },
          ]);
        }
      } catch (error) {
        console.error("Error checking database:", error);
        setMessages([
          {
            sender: "bot",
            text: "An error occurred while connecting to the server. Please try again later.",
          },
        ]);
      } finally {
        setIsWaiting(false);
      }
    };

    checkDatabase();
  }, []);

  const handleFileUpload = async (files) => {
    const formData = new FormData();
    Array.from(files).forEach((file) => formData.append("files", file));
  
    try {
      const response = await fetch(`${BACKEND_URL}/upload`, {
        method: "POST",
        body: formData,
      });
  
      if (response.ok) {
        setIsDataUploaded(true);
  
        setMessages((prevMessages) =>
          prevMessages.filter((message) => !message.showUploadButton)
        );
  
        setMessages((prevMessages) => [
          ...prevMessages,
          {
            sender: "bot",
            text: "Your Spotify data has been uploaded. You can now ask questions!",
          },
        ]);
      } else {
        const errorData = await response.json();
  
        setMessages((prevMessages) => [
          ...prevMessages,
          {
            sender: "bot",
            text: `Error: ${errorData.message}. Please try again.`,
            showUploadButton: true,
          },
        ]);
      }
    } catch (error) {
      console.error("Error uploading files:", error);
  
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          sender: "bot",
          text: "An error occurred while uploading your data. Please try again.",
          showUploadButton: true,
        },
      ]);
    }
  
    setShowUploadPopup(false);
  };
  
  const handleSendMessage = async (text) => {
    if (text.trim() === "" || !isDataUploaded || isWaiting) return;

    const newMessages = [...messages, { sender: "user", text }];
    setMessages(newMessages);
    setIsWaiting(true);

    try {
      const response = await fetch(`${BACKEND_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: text }),
      });

      if (response.ok) {
        const botResponse = await response.json();
        setMessages((prevMessages) => [
          ...prevMessages,
          { sender: "bot", text: botResponse.chatbot_response },
        ]);
      } else {
        setMessages((prevMessages) => [
          ...prevMessages,
          { sender: "bot", text: "An error occurred while processing your request." },
        ]);
      }
    } catch (error) {
      console.error("Error processing query:", error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "bot", text: "An error occurred while processing your request." },
      ]);
    } finally {
      setIsWaiting(false);
    }
  };

  return (
    <div className="App">
      <Header />
      <div className="chat-container">
        <ChatWindow messages={messages} onUploadClick={() => setShowUploadPopup(true)} />
        <InputBar
          onSendMessage={handleSendMessage}
          isDataUploaded={isDataUploaded}
          isWaiting={isWaiting}
        />
        {showUploadPopup && (
          <div className="upload-popup">
            <div className="upload-popup-content">
              <h3>Upload Your Spotify Data</h3>
              <input
                type="file"
                multiple
                accept=".json"
                onChange={(e) => handleFileUpload(e.target.files)}
              />
              <button onClick={() => setShowUploadPopup(false)}>Close</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;


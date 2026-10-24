import React from "react";
import "./ChatBubble.css";

function ChatBubble({ sender, text, showUploadButton, onUploadClick }) {
  const isUser = sender === "user";

  return (
    <div className={`chat-bubble-container ${isUser ? "user" : "bot"}`}>
      {!isUser && (
        <div className="bot-info">
          <img
            className="bot-avatar"
            src="/avatar.jpg"
            alt="Bot Avatar"
          />
          <span className="bot-name">Spotify Stats Bot</span>
        </div>
      )}
      <div className={`chat-bubble ${isUser ? "user" : "bot"}`}>
        <p>{text}</p>
        {!isUser && showUploadButton && (
          <button className="upload-button" onClick={onUploadClick}>
            Upload Data
          </button>
        )}
      </div>
    </div>
  );
}

export default ChatBubble;

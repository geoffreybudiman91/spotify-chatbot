import React, { useState, useRef } from "react";
import { Icon } from "@iconify/react";
import "./InputBar.css";

function InputBar({ onSendMessage, isDataUploaded, isWaiting }) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef(null);

  const handleInputChange = (e) => {
    setMessage(e.target.value);
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey && message.trim() !== "" && isDataUploaded && !isWaiting) {
      e.preventDefault();
      onSendMessage(message.trim());
      setMessage("");
    }
  };

  return (
    <div className="input-bar">
      <textarea
        ref={textareaRef}
        value={message}
        onChange={handleInputChange}
        onKeyDown={handleKeyPress}
        placeholder="Type a message..."
        disabled={!isDataUploaded || isWaiting} // Disable input if data isn't uploaded or waiting
      />
      <button
        onClick={() => {
          if (message.trim() !== "" && isDataUploaded && !isWaiting) {
            onSendMessage(message.trim());
            setMessage("");
          }
        }}
        disabled={!isDataUploaded || isWaiting} // Disable button if data isn't uploaded or waiting
        className={`send-button ${!isDataUploaded || isWaiting ? "disabled" : ""}`}
      >
        <Icon icon="material-symbols:send" />
      </button>
    </div>
  );
}

export default InputBar;

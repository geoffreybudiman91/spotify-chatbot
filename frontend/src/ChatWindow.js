import React, { useEffect, useRef } from "react";
import ChatBubble from "./ChatBubble";
import "./ChatWindow.css";

function ChatWindow({ messages, onUploadClick }) {
  const chatRef = useRef(null);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="chat-window" ref={chatRef}>
      {messages.map((message, index) => (
        <ChatBubble
          key={index}
          sender={message.sender}
          text={message.text}
          showUploadButton={message.showUploadButton}
          onUploadClick={onUploadClick}
        />
      ))}
    </div>
  );
}

export default ChatWindow;

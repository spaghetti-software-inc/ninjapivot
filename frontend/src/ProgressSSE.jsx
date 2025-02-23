import { useState, useEffect } from "react";

export default function SSEClient() {
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const eventSource = new EventSource("http://127.0.0.1:8000/sse/stream");

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setMessages((prevMessages) => [...prevMessages, data]);
      } catch (error) {
        console.error("Error parsing SSE data:", error);
      }
    };

    eventSource.onerror = (error) => {
      console.error("SSE Error:", error);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h2>📡 Live Streaming Data (SSE)</h2>
      <ul style={{ listStyleType: "none", padding: 0 }}>
        {messages.slice(-10).map((msg, index) => (
          <li key={index} style={{ margin: "5px 0", background: "#eee", padding: "10px", borderRadius: "5px" }}>
            ⏱ {new Date(msg.timestamp * 1000).toLocaleTimeString()} → 📊 {msg.value.toFixed(2)}
          </li>
        ))}
      </ul>
    </div>
  );
}

import { useRef, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";

export default function App() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hi 👋! Ask me anything about your Gmail emails." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollViewRef = useRef(null);

  // 🧠 IMPORTANT: Update this to YOUR computer's actual IP address
  // Find it by running:
  //   Windows: ipconfig
  //   Mac/Linux: ifconfig
  // For Android Emulator: use "10.0.2.2"
  // For iOS Simulator: use "localhost"
  const BACKEND_URL = "http://192.168.1.57:5000/chat"; 
  
  // 📝 Change "10.0.2.2" to your actual IP like "192.168.1.123"
  // Example: const BACKEND_URL = "http://192.168.1.123:5000/chat";

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    // Add user message
    const newMessages = [...messages, { sender: "user", text: input }];
    setMessages(newMessages);
    const query = input;
    setInput("");
    setLoading(true);

    try {
      console.log("🚀 Sending request to:", BACKEND_URL);
      console.log("📤 Query:", query);

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      const res = await fetch(BACKEND_URL, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Accept": "application/json",
        },
        body: JSON.stringify({ query }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      console.log("📥 Response status:", res.status);

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const data = await res.json();
      console.log("✅ Response data:", data);

      let botResponse = "";

      if (data.error) {
        botResponse = `⚠️ Error: ${data.error}`;
      } else if (Array.isArray(data.response)) {
        // If response is a list of emails
        if (data.response.length === 0) {
          botResponse = "No matching emails found. Try asking about meetings, orders, or reports.";
        } else {
          botResponse = data.response
            .map(
              (email) =>
                `📧 *${email.subject}*\nFrom: ${email.from}\n${email.snippet}`
            )
            .join("\n\n");
        }
      } else if (typeof data.response === 'string') {
        // If response is just a string
        botResponse = data.response;
      } else {
        botResponse = "Received unexpected response format.";
      }

      setMessages((prev) => [...prev, { sender: "bot", text: botResponse }]);
    } catch (error) {
      console.error("❌ Fetch error:", error);
      
      let errorMessage = "⚠️ Connection error! ";
      
      if (error.name === 'AbortError') {
        errorMessage += "Request timed out. Is your server running?";
      } else if (error.message.includes('Network request failed')) {
        errorMessage += `\n\nTroubleshooting:\n1. Check if backend is running (python app.py)\n2. Verify IP address is correct: ${BACKEND_URL}\n3. Make sure you're on the same WiFi network\n4. Try using 10.0.2.2 for Android emulator`;
      } else {
        errorMessage += error.message;
      }
      
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: errorMessage },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Test connection function
  const testConnection = async () => {
    const testUrl = BACKEND_URL.replace('/chat', '');
    try {
      const res = await fetch(testUrl, { method: 'GET' });
      const data = await res.json();
      Alert.alert(
        "Connection Test",
        `✅ Backend is reachable!\n\nStatus: ${data.status}\nMessage: ${data.message}`
      );
    } catch (error) {
      Alert.alert(
        "Connection Test Failed",
        `❌ Cannot reach backend at:\n${testUrl}\n\nError: ${error.message}\n\nMake sure:\n1. Backend is running\n2. IP address is correct\n3. You're on the same network`
      );
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header with connection test button */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Gmail AI Assistant</Text>
        <TouchableOpacity 
          style={styles.testButton} 
          onPress={testConnection}
        >
          <Text style={styles.testButtonText}>Test Connection</Text>
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.chatArea}
        ref={scrollViewRef}
        onContentSizeChange={() =>
          scrollViewRef.current?.scrollToEnd({ animated: true })
        }
      >
        {messages.map((msg, i) => (
          <View
            key={i}
            style={[
              styles.bubble,
              msg.sender === "user" ? styles.userBubble : styles.botBubble,
            ]}
          >
            <Text
              style={[
                styles.text,
                msg.sender === "user" ? styles.userText : styles.botText,
              ]}
            >
              {msg.text}
            </Text>
          </View>
        ))}
        
        {loading && (
          <View style={[styles.bubble, styles.botBubble]}>
            <ActivityIndicator size="small" color="#4a90e2" />
            <Text style={styles.loadingText}>Searching emails...</Text>
          </View>
        )}
      </ScrollView>

      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          placeholder="Ask about emails..."
          value={input}
          onChangeText={setInput}
          onSubmitEditing={sendMessage}
          returnKeyType="send"
          editable={!loading}
        />
        <TouchableOpacity 
          style={[styles.sendButton, loading && styles.sendButtonDisabled]} 
          onPress={sendMessage}
          disabled={loading}
        >
          <Text style={styles.sendButtonText}>
            {loading ? "..." : "Send"}
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

// 🎨 Styles
const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    backgroundColor: "#f5f5f5" 
  },
  header: {
    backgroundColor: "#4a90e2",
    padding: 15,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  headerTitle: {
    color: "white",
    fontSize: 18,
    fontWeight: "bold",
  },
  testButton: {
    backgroundColor: "rgba(255,255,255,0.2)",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 5,
  },
  testButtonText: {
    color: "white",
    fontSize: 12,
    fontWeight: "600",
  },
  chatArea: { 
    flex: 1, 
    padding: 10 
  },
  bubble: {
    marginVertical: 4,
    padding: 12,
    borderRadius: 12,
    maxWidth: "80%",
  },
  userBubble: {
    backgroundColor: "#4a90e2",
    alignSelf: "flex-end",
  },
  botBubble: {
    backgroundColor: "#e8e8e8",
    alignSelf: "flex-start",
  },
  text: {
    fontSize: 15,
    lineHeight: 20,
  },
  userText: {
    color: "white",
  },
  botText: {
    color: "#333",
  },
  loadingText: {
    marginLeft: 10,
    color: "#666",
    fontSize: 14,
  },
  inputRow: {
    flexDirection: "row",
    padding: 10,
    backgroundColor: "white",
    borderTopColor: "#ccc",
    borderTopWidth: 1,
  },
  input: {
    flex: 1,
    borderColor: "#ccc",
    borderWidth: 1,
    borderRadius: 10,
    paddingHorizontal: 15,
    height: 45,
    fontSize: 15,
  },
  sendButton: {
    backgroundColor: "#4a90e2",
    marginLeft: 10,
    paddingHorizontal: 20,
    justifyContent: "center",
    borderRadius: 10,
  },
  sendButtonDisabled: {
    backgroundColor: "#a0c4e8",
  },
  sendButtonText: {
    color: "white",
    fontWeight: "bold",
    fontSize: 15,
  },
});

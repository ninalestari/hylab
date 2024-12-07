from graphviz import Digraph

# Create a new directed graph
flowchart = Digraph("Face Recognition Flow", format='png')

# Set graph attributes
flowchart.attr(rankdir='TB', size='10')

# Add nodes representing the major steps in the code
flowchart.node("A", "Load Environment Variables")
flowchart.node("B", "Connect to MQTT Broker")
flowchart.node("C", "Receive MQTT Message")
flowchart.node("D", "Download Image from FTP")
flowchart.node("E", "Load Face Encodings")
flowchart.node("F", "Compare Faces")
flowchart.node("G", "Save Data to MongoDB")
flowchart.node("H", "Save Labeled Image")
flowchart.node("I", "Handle MQTT Disconnection")

# Add edges between nodes to represent the flow
flowchart.edge("A", "B")
flowchart.edge("B", "C")
flowchart.edge("C", "D")
flowchart.edge("D", "E")
flowchart.edge("E", "F")
flowchart.edge("F", "G", label="Match Found")
flowchart.edge("F", "H", label="Label Image")
flowchart.edge("F", "I", label="No Match Found")

# Render the flowchart to a file
flowchart.render("face_recognition_flowchart")

print("Flowchart created and saved as 'face_recognition_flowchart.png'")

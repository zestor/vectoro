# Vectoro - The Next-Generation Vector Database 🚀

## License None

Welcome to Vectoro, your ultimate solution for managing, persisting, and manipulating vectors with utmost ease. Designed with developers in mind, Vectoro lets you focus on what you do best - building applications, while it takes care of the complex vector operations in the background. With a fast and secure RESTful API based on FastAPI, an intuitive web interface for managing vector instances, and persistent storage using JSON, Vectoro is your go-to solution for all things vector! 🚀👨‍💻

Structure
Vectoro is designed as a modular system for scalability and ease of use, and consists of four main components:

vectoro.py: The core vector database engine, supporting all CRUD operations and providing the backbone for Vectoro. 🎛️🔩

vectoro_server.py: A FastAPI interface that sits on top of the Vectoro engine, enabling external applications to communicate with the database through a secure and high-speed RESTful API. 🌐📡

vectoro_client.py: A pre-packaged client application to make HTTP requests to the Vectoro server, offering a hassle-free way of testing and interacting with the database. 📬🤖

webapp.py: A user-friendly frontend that offers a visual management interface for vector instances, allowing you to monitor and manage your vector database from the comfort of your web browser. 🖥️🐭
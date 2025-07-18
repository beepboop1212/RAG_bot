<p align="center"><h1 align="center">RAG_BOT</h1></p>
<p align="center">
	<em><code>❯ Rishvanth G V</code></em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/last-commit/beepboop1212/RAG_bot?style=default&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/beepboop1212/RAG_bot?style=default&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/beepboop1212/RAG_bot?style=default&color=0080ff" alt="repo-language-count">
</p>
<p align="center"><!-- default option, no dependency badges. -->
</p>
<p align="center">
	<!-- default option, no dependency badges. -->
</p>
<br>

## 🔗 Table of Contents

- [📍 Overview](#-overview)
- [👾 Features](#-features)
- [📁 Project Structure](#-project-structure)
  - [📂 Project Index](#-project-index)
- [🚀 Getting Started](#-getting-started)
  - [☑️ Prerequisites](#-prerequisites)
  - [⚙️ Installation](#-installation)
  - [🤖 Usage](#🤖-usage)
  - [🧪 Testing](#🧪-testing)
- [📌 Project Roadmap](#-project-roadmap)
- [🔰 Contributing](#-contributing)
- [🎗 License](#-license)
- [🙌 Acknowledgments](#-acknowledgments)

---

## 📍 Overview

<code>❯ REPLACE-ME</code>

---

## 👾 Features

<code>❯ REPLACE-ME</code>

---

## 📁 Project Structure

```sh
└── RAG_bot/
    ├── README.md
    ├── bbox
    │   ├── box.py
    │   └── output_with_boxes.png
    ├── project
    │   ├── README.md
    │   ├── backend
    │   ├── frontend
    │   └── requirements.txt
    └── quizr
        └── quiz.py
```


<details> <!-- __root__ Submodule -->
	<summary><b>__root__</b></summary>
	<blockquote>
		<table>
		</table>
	</blockquote>
</details>

<details> <!-- quizr Submodule -->
	<summary><b>quizr</b></summary>
	<blockquote>
		<table>
		<tr>
			<td><b><a href='https://github.com/beepboop1212/RAG_bot/blob/master/quizr/quiz.py'>quiz.py</a></b></td>
			<td><code>The main Streamlit application file for the Quizzer App. Handles UI, URL input, web scraping, and LLM interaction.</code></td>
		</tr>
		</table>
	</blockquote>
</details>

<details> <!-- project Submodule -->
	<summary><b>project</b></summary>
	<blockquote>
		<table>
		<tr>
			<td><b><a href='https://github.com/beepboop1212/RAG_bot/blob/master/project/requirements.txt'>requirements.txt</a></b></td>
			<td><code>Lists all Python dependencies for the RAG Bot project (both frontend and backend).</code></td>
		</tr>
		</table>

		- 📁 project  
  - 📄 [requirements.txt](https://github.com/beepboop1212/RAG_bot/blob/master/project/requirements.txt)  
    <sub><code>Lists all Python dependencies for the RAG Bot project (both frontend and backend).</code></sub>

  - 📁 backend  
    - 📄 [run_backend.py](https://github.com/beepboop1212/RAG_bot/blob/master/project/backend/run_backend.py)  
      <sub><code>Entry point to launch the FastAPI backend server using Uvicorn.</code></sub>

    - 📁 app  
      - 📄 [main.py](https://github.com/beepboop1212/RAG_bot/blob/master/project/backend/app/main.py)  
        <sub><code>The core FastAPI application instance. Mounts the main API router and configures middleware.</code></sub>

      - 📁 schemas  
        - 📄 [user.py](https://github.com/beepboop1212/RAG_bot/blob/master/project/backend/app/schemas/user.py)  
          <sub><code>Pydantic schema defining the data model and validation rules for a User.</code></sub>
        - 📄 [session.py](https://github.com/beepboop1212/RAG_bot/blob/master/project/backend/app/schemas/session.py)  
          <sub><code>Pydantic schema for a chat Session, linking messages to a user.</code></sub>
        - 📄 [message.py](https://github.com/beepboop1212/RAG_bot/blob/master/project/backend/app/schemas/message.py)  
          <sub><code>Pydantic schema for a single Message within a chat session.</code></sub>

      - 📁 core  
        - 📄 [config.py](https://github.com/beepboop1212/RAG_bot/blob/master/project/backend/app/core/config.py)  
          <sub><code>Loads secrets like API keys and database URLs from environment variables.</code></sub>

      - 📁 services  
        - 📄 [chat_service.py](https://github.com/beepboop1212/RAG_bot/blob/master/project/backend/app/services/chat_service.py)  
          <sub><code>Business logic for RAG pipeline, chat processing, and LLM calls.</code></sub>

      - 📁 api  
        - 📁 v1  
          - 📄 [api.py](https://github.com/beepboop1212/RAG_bot/blob/master/project/backend/app/api/v1/api.py)  
            <sub><code>Main API router (v1) that includes sub-routers (chat, users, sessions).</code></sub>
          - 📁 endpoints  
            - 📄 [sessions.py](https://github.com/beepboop1212/RAG_bot/blob/master/project/backend/app/api/v1/endpoints/sessions.py)  
              <sub><code>Endpoints for chat session creation, retrieval, and management.</code></sub>
            - 📄 [chat.py](https://github.com/beepboop1212/RAG_bot/blob/master/project/backend/app/api/v1/endpoints/chat.py)  
              <sub><code>Handles incoming messages and returns LLM-generated responses.</code></sub>
            - 📄 [users.py](https://github.com/beepboop1212/RAG_bot/blob/master/project/backend/app/api/v1/endpoints/users.py)  
              <sub><code>User-related endpoints like creation and lookup.</code></sub>

      - 📁 db  
        - 📄 [database.py](https://github.com/beepboop1212/RAG_bot/blob/master/project/backend/app/db/database.py)  
          <sub><code>Sets up the database engine and session management.</code></sub>
        - 📄 [crud.py](https://github.com/beepboop1212/RAG_bot/blob/master/project/backend/app/db/crud.py)  
          <sub><code>CRUD operations to interact with DB tables.</code></sub>
        - 📄 [models.py](https://github.com/beepboop1212/RAG_bot/blob/master/project/backend/app/db/models.py)  
          <sub><code>Defines the SQLAlchemy ORM models.</code></sub>

  - 📁 frontend  
    - 📄 [app.py](https://github.com/beepboop1212/RAG_bot/blob/master/project/frontend/app.py)  
      <sub><code>Streamlit UI for the RAG Bot's chat interface.</code></sub>
    - 📄 [api_client.py](https://github.com/beepboop1212/RAG_bot/blob/master/project/frontend/api_client.py)  
      <sub><code>Communicates between frontend and FastAPI backend.</code></sub>

<details> <!-- bbox Submodule -->
	<summary><b>bbox</b></summary>
	<blockquote>
		<table>
		<tr>
			<td><b><a href='https://github.com/beepboop1212/RAG_bot/blob/master/bbox/box.py'>box.py</a></b></td>
			<td><code>The script for the Bounding Box generator. Contains logic to call the multimodal LLM, parse coordinates, and draw boxes on the image.</code></td>
		</tr>
		</table>
	</blockquote>
</details>


---
## 🚀 Getting Started

### ☑️ Prerequisites

Before getting started with RAG_bot, ensure your runtime environment meets the following requirements:

- **Programming Language:** Python
- **Package Manager:** Pip


### ⚙️ Installation

Install RAG_bot using one of the following methods:

**Build from source:**

1. Clone the RAG_bot repository:
```sh
❯ git clone https://github.com/beepboop1212/RAG_bot
```

2. Navigate to the project directory:
```sh
❯ cd RAG_bot
```

3. Install the project dependencies:


**Using `pip`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Pip-3776AB.svg?style={badge_style}&logo=pypi&logoColor=white" />](https://pypi.org/project/pip/)

```sh
❯ pip install -r project/requirements.txt
```




### 🤖 Usage
Run RAG_bot using the following command:
**Using `pip`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Pip-3776AB.svg?style={badge_style}&logo=pypi&logoColor=white" />](https://pypi.org/project/pip/)

```sh
❯ python {entrypoint}
```


### 🧪 Testing
Run the test suite using the following command:
**Using `pip`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Pip-3776AB.svg?style={badge_style}&logo=pypi&logoColor=white" />](https://pypi.org/project/pip/)

```sh
❯ pytest
```


---
## 📌 Project Roadmap

- [1] **`RAG Bot`**:
    Dockerize the frontend and backend for easy deployment.
    Implement user authentication and authorization.
    Add support for more data sources (PDFs, DOCX) for the RAG pipeline.
  
- [2] **`Quizzer App`**: 
    Allow users to upload documents (PDF, DOCX) in addition to URLs.
    Add options for different quiz types (e.g., multiple choice, true/false).
    Implement a scoring and feedback mechanism.
  
- [3] **`Bounding Box Generator`**:
    Experiment with different multimodal models to improve accuracy.
    Create a hybrid system that uses a traditional CV model for initial detection and an LLM for refinement.
    Develop a Streamlit interface for interactive image uploads.

---

## 🔰 Contributing

- **💬 [Join the Discussions](https://github.com/beepboop1212/RAG_bot/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/beepboop1212/RAG_bot/issues)**: Submit bugs found or log feature requests for the `RAG_bot` project.
- **💡 [Submit Pull Requests](https://github.com/beepboop1212/RAG_bot/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/beepboop1212/RAG_bot
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/beepboop1212/RAG_bot/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=beepboop1212/RAG_bot">
   </a>
</p>
</details>

---

## 🎗 License

This project is not licensed

---

## 🙌 Acknowledgments

Cyces Team

---

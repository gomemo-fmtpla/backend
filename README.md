[<img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" align="left" width="20%" padding="20">]()

## &nbsp;&nbsp; BACKEND

&nbsp;&nbsp;&nbsp;&nbsp; ***Backend: Powering Your Ideas with Seamless Precision***

<p align="left">&nbsp;&nbsp;
	<img src="https://img.shields.io/github/license/gomemo-fmtpla/backend?style=flat-square&logo=opensourceinitiative&logoColor=white&color=A931EC" alt="license">
	<img src="https://img.shields.io/github/last-commit/gomemo-fmtpla/backend?style=flat-square&logo=git&logoColor=white&color=A931EC" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/gomemo-fmtpla/backend?style=flat-square&color=A931EC" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/gomemo-fmtpla/backend?style=flat-square&color=A931EC" alt="repo-language-count">
</p>
<br>

<details><summary>Table of Contents</summary>

- [ Overview](#-overview)
- [ Features](#-features)
- [ Project Structure](#-project-structure)
  - [ Project Index](#-project-index)
- [ Getting Started](#-getting-started)
  - [ Prerequisites](#-prerequisites)
  - [ Installation](#-installation)
  - [ Usage](#-usage)
  - [ Testing](#-testing)
- [ Project Roadmap](#-project-roadmap)
- [ Contributing](#-contributing)
- [ License](#-license)
- [ Acknowledgments](#-acknowledgments)

</details>
<hr>

##  Overview

This software project is designed to streamline the process of managing and deploying web applications, making it an ideal solution for developers and tech teams seeking efficiency and consistency. At its core, the project leverages a robust set of tools and configurations to simplify database management, application deployment, and environment setup. By utilizing Docker for containerization, Alembic for seamless database migrations, and a comprehensive set of dependencies outlined in the requirements file, the project ensures a smooth and uniform experience across different systems. The target audience includes software developers and IT professionals who are looking for a reliable and scalable way to manage their web applications, reduce deployment friction, and maintain a high level of code quality and consistency. This project stands out by offering a cohesive and integrated approach to modern web application development, making it a valuable asset for any development team.

---

##  Features

|      | Feature         | Summary       |
| :--- | :---:           | :---          |
| ⚙️  | **Architecture**  | <ul><li>Microservices architecture using FastAPI</li><li>Containerized with Docker for consistent deployment</li><li>Relational database management with SQLAlchemy and Alembic</li></ul> |
| 🔩 | **Code Quality**  | <ul><li>Pythonic code style with PEP 8 compliance</li><li>Use of type hints with Pydantic for data validation</li><li>Continuous integration with automated testing</li></ul> |
| 📄 | **Documentation** | <ul><li>Comprehensive installation and usage guides</li><li>Codebase primarily in Python with 38 `.py` files</li><li>Documentation for environment setup using `requirements.txt` and Docker</li></ul> |
| 🔌 | **Integrations**  | <ul><li>OpenAI and Google Generative AI for AI capabilities</li><li>MinIO for object storage</li><li>YouTube Transcript API for multimedia processing</li></ul> |
| 🧩 | **Modularity**    | <ul><li>Separation of concerns with modular Python packages</li><li>Use of FastAPI for modular route handling</li><li>Database migrations managed by Alembic</li></ul> |
| 🧪 | **Testing**       | <ul><li>Automated testing with Pytest</li><li>Test commands integrated into CI pipeline</li><li>Mocking and test coverage for API endpoints</li></ul> |
| ⚡️  | **Performance**   | <ul><li>Asynchronous request handling with FastAPI and Uvicorn</li><li>Efficient database queries with SQLAlchemy</li><li>Optimized multimedia processing with FFmpeg and Pydub</li></ul> |
| 🛡️ | **Security**      | <ul><li>Password hashing with Bcrypt and Passlib</li><li>Environment variable management with Python-dotenv</li><li>Secure API endpoints with authentication and authorization</li></ul> |
| 📦 | **Dependencies**  | <ul><li>Managed with `pip` and `requirements.txt`</li><li>Key libraries include FastAPI, SQLAlchemy, and Pydantic</li><li>Dockerfile for containerized environments</li></ul> |
| 🚀 | **Scalability**   | <ul><li>Scalable microservices architecture</li><li>Horizontal scaling with Docker containers</li><li>Load balancing capabilities with Uvicorn</li></ul> |

---

##  Project Structure

```sh
└── backend/
    ├── Dockerfile
    ├── Dockerfile2
    ├── Makefile
    ├── alembic
    │   ├── README
    │   ├── env.py
    │   ├── script.py.mako
    │   └── versions
    ├── alembic.ini
    ├── app
    │   ├── commons
    │   ├── database
    │   ├── main.py
    │   ├── route
    │   └── usecases
    ├── requirements.txt
    ├── temp.mp3
    │   └── 14 UNIQUE Mac Apps You Can’t Live Without!.mp3
    └── tests
        └── test_user_crud.py
```


###  Project Index
<details open>
	<summary><b><code>BACKEND/</code></b></summary>
	<details> <!-- __root__ Submodule -->
		<summary><b>__root__</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/requirements.txt'>requirements.txt</a></b></td>
				<td>- Define the project's dependencies, facilitating the installation and management of required packages for the application<br>- These dependencies support various functionalities, including web framework operations, environment management, database interactions, API integrations, security, and multimedia processing<br>- By specifying these packages, the file ensures a consistent development environment and aids in the deployment process across different systems within the project's architecture.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/alembic.ini'>alembic.ini</a></b></td>
				<td>- Facilitates database migration management by configuring Alembic settings for a single database setup<br>- Specifies paths for migration scripts, version control, and logging configurations<br>- Enables customization of migration file naming and timezone settings<br>- Integrates with PostgreSQL using environment variables for database credentials<br>- Supports post-write hooks for code formatting and linting, enhancing the maintainability and consistency of database schema changes within the project.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/Dockerfile'>Dockerfile</a></b></td>
				<td>- Facilitates the deployment of a Python-based application using Docker by setting up a containerized environment<br>- It installs necessary dependencies, copies application files, and configures the server to run with Uvicorn on port 3657<br>- This setup ensures consistency across different environments, streamlining the development and deployment process within the project's architecture.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/Makefile'>Makefile</a></b></td>
				<td>- Facilitates development and deployment tasks within the project by providing commands for running the application in development mode, executing tests, installing dependencies, and managing database migrations<br>- Enhances workflow efficiency by automating routine processes, ensuring that developers can focus on building features while maintaining consistency across the codebase<br>- Integral to maintaining streamlined operations and supporting continuous integration and delivery practices.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/Dockerfile2'>Dockerfile2</a></b></td>
				<td>- Facilitate the deployment of a Python-based application by defining a Docker container environment<br>- Utilize a Python 3.11 base image, install necessary dependencies, and configure the application to run with Uvicorn<br>- Include provisions for Squid proxy configuration and expose port 8000 for network access<br>- This setup ensures a consistent and isolated environment for running the application within the project's architecture.</td>
			</tr>
			</table>
		</blockquote>
	</details>
	<details> <!-- app Submodule -->
		<summary><b>app</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/main.py'>main.py</a></b></td>
				<td>- Initialize and configure a FastAPI application by loading environment variables and setting up API routes for user and note functionalities<br>- The application is prepared to run on a specified host and port using Uvicorn<br>- This setup is integral to the project's architecture, facilitating modular route management and ensuring the application is ready for deployment and scalable API interactions.</td>
			</tr>
			</table>
			<details>
				<summary><b>database</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/database/db.py'>db.py</a></b></td>
						<td>- Establishes a singleton database connection using SQLAlchemy, ensuring efficient resource management and consistent access across the application<br>- By configuring the connection with environment variables, it supports flexible deployment environments<br>- The setup provides a session factory for database interactions and a declarative base for ORM models, forming the backbone of the application's data layer within the overall architecture.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/database/models.py'>models.py</a></b></td>
						<td>- Defines the database models for a note-taking application, establishing the structure and relationships between users, folders, notes, and note metadata<br>- Facilitates user management, note organization, and metadata association, supporting features like subscription tracking, content categorization, and multilingual capabilities<br>- Serves as a foundational component for data storage and retrieval within the broader application architecture.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/database/1.sql'>1.sql</a></b></td>
						<td>- Define the database schema for managing user accounts, folders, and notes within the application<br>- Establishes relationships between users, folders, and notes, including constraints for data integrity<br>- Supports subscription management through an enum type for subscription plans<br>- Facilitates efficient data retrieval with indexes on key columns, enhancing the application's ability to organize and access user-generated content effectively.</td>
					</tr>
					</table>
					<details>
						<summary><b>schemas</b></summary>
						<blockquote>
							<table>
							<tr>
								<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/database/schemas/user.py'>user.py</a></b></td>
								<td>- Defines data models for user-related operations within the application, focusing on user creation and updates<br>- Utilizes Pydantic for data validation and serialization, ensuring that user information such as username, email, subscription plan, and transaction receipt is accurately managed<br>- Plays a crucial role in maintaining data integrity and consistency across the user management system, aligning with the broader architecture of the project.</td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/database/schemas/note.py'>note.py</a></b></td>
								<td>- Defines data models for notes within the application, facilitating the creation, updating, and retrieval of note information<br>- These models include attributes such as title, summary, transcript text, language, and optional content like flashcards and quizzes<br>- By leveraging Pydantic for data validation and serialization, it ensures consistent data handling across the application, supporting efficient interaction with the database and enhancing the overall data management architecture.</td>
							</tr>
							</table>
						</blockquote>
					</details>
				</blockquote>
			</details>
			<details>
				<summary><b>route</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/route/user.py'>user.py</a></b></td>
						<td>- Manages user-related operations within the application, including authentication, subscription management, and user deletion<br>- Facilitates user creation with a welcoming note, updates subscription details, and ensures secure password handling<br>- Integrates with authentication and database modules to maintain user data integrity and security<br>- Supports user lifecycle management by handling user data retrieval, updates, and deletions while ensuring associated resources are appropriately managed.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/route/quiz.py'>quiz.py</a></b></td>
						<td>- Facilitates the generation of quizzes from YouTube video transcripts by providing an API endpoint<br>- It integrates with the transcript extraction and quiz generation use cases to process a given transcript, ensuring successful extraction before generating quizzes<br>- This functionality is part of the broader application architecture, enabling dynamic content creation and enhancing user engagement through interactive quiz experiences.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/route/summary.py'>summary.py</a></b></td>
						<td>- Facilitates the generation of summaries and transcripts from YouTube videos and audio inputs within the application<br>- It outlines endpoints for processing YouTube URLs and audio transcripts, leveraging external functions for transcription and summary generation<br>- The module is designed to handle requests, manage authentication, and ensure successful processing, contributing to the broader functionality of content analysis and summarization in the codebase.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/route/flashcard.py'>flashcard.py</a></b></td>
						<td>- Facilitates the creation of flashcards from transcripts by defining an API endpoint within the application<br>- It processes incoming requests containing transcripts, utilizes the transcript extraction and flashcard generation use cases, and returns the generated flashcards<br>- This functionality supports the broader project architecture by enabling users to transform textual content into educational flashcards, enhancing the application's learning and study capabilities.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/route/note.py'>note.py</a></b></td>
						<td>- The file `app/route/note.py` serves as a crucial component in the project's architecture by defining the API endpoints related to note management<br>- It facilitates the creation, retrieval, updating, and management of notes within the application<br>- This file integrates various functionalities such as metadata handling, note addition, and updates, as well as advanced features like audio transcription and summary generation<br>- By leveraging FastAPI's routing capabilities, it ensures secure and efficient interaction with the database through dependency injection and authentication guards<br>- This file is integral to the user-facing aspect of the application, enabling seamless note-related operations and enhancing the overall user experience.</td>
					</tr>
					</table>
				</blockquote>
			</details>
			<details>
				<summary><b>commons</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/commons/environment_manager.py'>environment_manager.py</a></b></td>
						<td>- Environment management is facilitated by dynamically loading environment-specific configurations based on the current environment setting<br>- By utilizing the dotenv library, it ensures that the appropriate environment variables are loaded, whether in development or production<br>- This approach enhances flexibility and maintainability across different deployment stages, allowing the application to adapt its behavior according to the specified environment, thereby supporting the overall architecture's modularity and scalability.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/commons/logger.py'>logger.py</a></b></td>
						<td>- Facilitates centralized logging functionality across the application by configuring a logger to capture and store log messages in a specified format and location<br>- Enhances error tracking and debugging by integrating with the Uvicorn server's error logging system<br>- Contributes to the overall maintainability and observability of the codebase by ensuring consistent logging practices, which are crucial for monitoring application behavior and diagnosing issues.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/commons/pydantic_to_json.py'>pydantic_to_json.py</a></b></td>
						<td>- Facilitates the conversion of Note and NoteMetadata objects into dictionary format, enabling seamless integration with JSON-based operations within the application<br>- This functionality supports data serialization, making it easier to handle and manipulate note-related data across different components of the project<br>- By providing a structured representation of notes and their metadata, it enhances data interchange and storage processes within the overall architecture.</td>
					</tr>
					</table>
				</blockquote>
			</details>
			<details>
				<summary><b>usecases</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/usecases/auth_guard.py'>auth_guard.py</a></b></td>
						<td>- Ensure secure access to the application by verifying API keys and user existence within the database<br>- The authentication guard function facilitates user authentication, raising exceptions for missing or invalid credentials<br>- It integrates with the broader architecture by depending on the database session and user retrieval logic, maintaining a consistent security layer across the application.</td>
					</tr>
					</table>
					<details>
						<summary><b>misc</b></summary>
						<blockquote>
							<table>
							<tr>
								<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/usecases/misc/summary_generation_vertex.py'>summary_generation_vertex.py</a></b></td>
								<td>- Facilitates the generation of summaries from transcripts using the ChatVertexAI model<br>- It aims to transform lengthy transcripts into concise Markdown summaries, enhancing readability and accessibility within the application<br>- By leveraging the Gemini-1.5-pro model, it provides a structured approach to summarization, contributing to the broader goal of efficient data processing and presentation in the project's architecture.</td>
							</tr>
							</table>
						</blockquote>
					</details>
					<details>
						<summary><b>note</b></summary>
						<blockquote>
							<table>
							<tr>
								<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/usecases/note/note.py'>note.py</a></b></td>
								<td>- Facilitates the creation, updating, and management of notes and their metadata within the Gomemo application<br>- It supports adding new notes, updating existing ones, managing note metadata, and organizing notes into folders<br>- Additionally, it provides functionality for creating a welcoming note for new users, enhancing the user experience by offering a structured introduction to the app's features and capabilities.</td>
							</tr>
							</table>
						</blockquote>
					</details>
					<details>
						<summary><b>user</b></summary>
						<blockquote>
							<table>
							<tr>
								<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/usecases/user/user.py'>user.py</a></b></td>
								<td>- User management functionality is provided by handling operations such as retrieving, creating, and updating user information within the database<br>- It supports fetching users by ID, username, or email, and includes methods for creating new users and updating existing ones<br>- Additionally, it offers a way to check a user's subscription status, integrating with the broader system to manage user-related data efficiently.</td>
							</tr>
							</table>
						</blockquote>
					</details>
					<details>
						<summary><b>storage</b></summary>
						<blockquote>
							<table>
							<tr>
								<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/usecases/storage/audio_store.py'>audio_store.py</a></b></td>
								<td>- Facilitates audio file management within the project by providing functionalities to upload, download, and delete audio files using MinIO storage<br>- It generates public URLs for uploaded files, handles file operations from URLs, and ensures secure access through environment-managed credentials<br>- The module also includes error handling for file operations, enhancing the robustness and reliability of the storage interactions in the application.</td>
							</tr>
							</table>
						</blockquote>
					</details>
					<details>
						<summary><b>generation</b></summary>
						<blockquote>
							<table>
							<tr>
								<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/usecases/generation/summary_generation.py'>summary_generation.py</a></b></td>
								<td>- Summary generation functionality leverages OpenAI's API to create detailed markdown summaries from transcripts<br>- It includes features like language detection, categorization, and emoji representation<br>- The output is structured in JSON format, ensuring a well-organized summary with titles, subheadings, and key points<br>- This component enhances the project by providing automated, context-aware content summarization, improving user engagement and content accessibility.</td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/usecases/generation/flashcard_generation.py'>flashcard_generation.py</a></b></td>
								<td>- Generate flashcards from a given transcript using OpenAI's language model, facilitating language autodetection if unspecified<br>- This functionality supports the broader project architecture by enabling automated educational content creation, enhancing user engagement through interactive learning tools<br>- The process ensures structured output by adhering to a predefined JSON schema, contributing to the project's goal of leveraging AI for personalized and accessible learning experiences.</td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/usecases/generation/summary_translation_generation.py'>summary_translation_generation.py</a></b></td>
								<td>- Facilitates the translation of summaries into different languages using OpenAI's API, enhancing the accessibility and usability of content across diverse linguistic audiences<br>- By integrating with the broader codebase, it supports multilingual capabilities, ensuring that users can interact with and understand content in their preferred language, thereby broadening the reach and impact of the project.</td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/usecases/generation/youtube_transcript_extraction.py'>youtube_transcript_extraction.py</a></b></td>
								<td>- Facilitates the extraction and generation of transcripts from YouTube videos by utilizing various methods, including direct subtitle retrieval and audio transcription via external services<br>- Enhances accessibility and content analysis within the project by providing structured text data from video content, supporting error handling and fallback mechanisms to ensure reliable transcript generation even when initial methods fail.</td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/usecases/generation/audio_transcribe_extraction.py'>audio_transcribe_extraction.py</a></b></td>
								<td>- Facilitates audio transcription by leveraging both a local Whisper model and OpenAI's transcription service<br>- It handles downloading audio files, processing them for transcription, and returning the results<br>- Additionally, it provides functionality to print audio file information<br>- This component plays a crucial role in enabling audio data extraction and analysis within the broader application architecture, supporting features that require audio-to-text conversion.</td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/app/usecases/generation/quiz_generation.py'>quiz_generation.py</a></b></td>
								<td>- Quiz generation functionality leverages OpenAI's capabilities to create multiple-choice quizzes from a given transcript<br>- It supports language detection and customization, ensuring quizzes are generated in the appropriate language<br>- This component is integral to the application's educational tools, enhancing user engagement by transforming content into interactive learning experiences<br>- Error handling ensures robustness, providing feedback in case of generation failures.</td>
							</tr>
							</table>
						</blockquote>
					</details>
				</blockquote>
			</details>
		</blockquote>
	</details>
	<details> <!-- alembic Submodule -->
		<summary><b>alembic</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/alembic/script.py.mako'>script.py.mako</a></b></td>
				<td>- Facilitates database schema migrations within the project by defining revision identifiers and upgrade/downgrade functions<br>- Utilizes Alembic, a lightweight database migration tool for SQLAlchemy, to manage changes to the database schema over time<br>- Supports version control of database changes, ensuring consistency and traceability across different environments, which is crucial for maintaining the integrity and evolution of the database structure in the codebase.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/alembic/env.py'>env.py</a></b></td>
				<td>- Facilitates database schema migrations using Alembic by configuring the migration environment with necessary database connection details<br>- It dynamically constructs the database URL from environment variables and sets up logging<br>- The script supports both offline and online migration modes, ensuring that the database schema stays in sync with the application's models, which are imported for autogeneration support.</td>
			</tr>
			</table>
			<details>
				<summary><b>versions</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/alembic/versions/daa4d6319534_adding_folder_and_user_id_on_metadata.py'>daa4d6319534_adding_folder_and_user_id_on_metadata.py</a></b></td>
						<td>- Introduce enhancements to the database schema by adding folder and user ID fields to the metadata table<br>- This migration script, part of the Alembic version control system, facilitates schema evolution without disrupting the existing data integrity<br>- It aligns with the project's architecture by ensuring that database changes are systematically tracked and reversible, supporting ongoing development and feature expansion.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/alembic/versions/649391dfd01a_change_yt_link_to_content_url.py'>649391dfd01a_change_yt_link_to_content_url.py</a></b></td>
						<td>- Facilitates a database schema migration by replacing the 'youtube_link' column with a 'content_url' column in the 'notes' table<br>- This change reflects a broader shift in the project to accommodate diverse content types beyond YouTube links, enhancing flexibility in how content is referenced and stored<br>- The migration ensures backward compatibility by providing both upgrade and downgrade paths for the database schema.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/alembic/versions/3e98b8300152_initial_migrate.py'>3e98b8300152_initial_migrate.py</a></b></td>
						<td>- Establishes the initial database schema for the project by creating tables for users, folders, and notes, along with their respective relationships and constraints<br>- This migration sets up essential structures for managing user accounts, organizing content into folders, and storing detailed notes, including metadata like flashcards and quizzes<br>- It forms the foundational layer for data persistence and retrieval within the application's architecture.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/alembic/versions/4f6ef13845a0_adding_metadata.py'>4f6ef13845a0_adding_metadata.py</a></b></td>
						<td>- Introduce a new database table, `note_metadata`, to store additional information about notes, such as title, content category, emoji representation, and creation date<br>- This enhancement supports better organization and categorization of notes within the application<br>- The migration script ensures seamless integration of this new table into the existing database schema, maintaining data integrity through foreign key constraints and primary key definitions.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/alembic/versions/b4a0a6a94c2a_.py'>b4a0a6a94c2a_.py</a></b></td>
						<td>- Manage database schema migrations within the project by utilizing Alembic, a database migration tool for SQLAlchemy<br>- The file represents a specific migration revision, identified by a unique ID, and provides placeholders for upgrade and downgrade functions<br>- These functions facilitate schema changes, ensuring the database structure aligns with the application's evolving requirements while maintaining version control and traceability.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/alembic/versions/e2f0353d8e44_.py'>e2f0353d8e44_.py</a></b></td>
						<td>- Introduce a new column, 'transaction_receipt', to the 'users' table in the database schema, enhancing the data model to accommodate transaction-related information<br>- This migration script, part of the Alembic versioning system, ensures that the database schema evolves in a controlled manner, supporting the project's ongoing development and feature expansion while maintaining backward compatibility through the ability to downgrade changes if necessary.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/alembic/versions/e0c5dda9fcb2_.py'>e0c5dda9fcb2_.py</a></b></td>
						<td>- Enhances the database schema by adding `user_id` and `folder_id` columns to the `note_metadata` table, establishing foreign key relationships with the `users` and `folders` tables<br>- This migration facilitates better data organization and retrieval by linking notes to specific users and folders, aligning with the project's goal of improving data management and relational integrity within the application's architecture.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/alembic/versions/cc2bd32b1d9f_.py'>cc2bd32b1d9f_.py</a></b></td>
						<td>- Manage database schema migrations within the project by utilizing Alembic<br>- The file serves as a version control mechanism for the database, allowing for upgrades and downgrades of the schema<br>- It ensures that changes to the database structure are tracked and can be applied or reverted as needed, maintaining consistency and integrity across different environments in the codebase architecture.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/alembic/versions/20a20c7f71f5_.py'>20a20c7f71f5_.py</a></b></td>
						<td>- Facilitates a database schema migration by altering the 'subscription_plan' column in the 'users' table from an ENUM type to a String type<br>- This change is part of the project's ongoing efforts to enhance flexibility in handling subscription plans<br>- The migration ensures that the database structure aligns with evolving application requirements, supporting future feature development and improving overall system adaptability.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/alembic/versions/96dbf61620e1_change_email_to_not_unique.py'>96dbf61620e1_change_email_to_not_unique.py</a></b></td>
						<td>- Modify the database schema to change the email field in the users table from unique to non-unique<br>- This adjustment allows multiple users to have the same email address, enhancing flexibility in user management<br>- The migration script includes both upgrade and downgrade functions to apply or revert the change, ensuring smooth transitions between different database states within the project's architecture.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/alembic/versions/55fe4ec769a2_.py'>55fe4ec769a2_.py</a></b></td>
						<td>- Introduce a new boolean column, 'translated', to the 'notes' table within the database schema, initially setting its value to false for all existing records<br>- This migration script, part of the Alembic versioning system, ensures the database schema evolves in a controlled manner, supporting new application features while maintaining backward compatibility<br>- The script also provides a downgrade path to remove the column if necessary.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/alembic/versions/c096c4ab76ef_updating_content_url_size.py'>c096c4ab76ef_updating_content_url_size.py</a></b></td>
						<td>- Update the database schema by altering the 'content_url' column size in the 'notes' table from 255 to 1024 characters<br>- This change accommodates longer URLs, enhancing the system's ability to store more extensive content links<br>- It is part of the migration process managed by Alembic, ensuring database consistency and supporting the evolving needs of the application within the overall architecture.</td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/gomemo-fmtpla/backend/blob/master/alembic/versions/b2598f737b6d_adding_youtube_link_col.py'>b2598f737b6d_adding_youtube_link_col.py</a></b></td>
						<td>- Introduce a new column, 'youtube_link', to the 'notes' table within the database schema, enhancing the application's ability to store and manage YouTube links associated with notes<br>- This migration script, part of the Alembic version control system, supports both upgrading and downgrading the database schema, ensuring seamless integration and rollback capabilities within the broader project architecture.</td>
					</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
</details>

---
##  Getting Started

###  Prerequisites

Before getting started with backend, ensure your runtime environment meets the following requirements:

- **Programming Language:** Python
- **Package Manager:** Pip
- **Container Runtime:** Docker


###  Installation

Install backend using one of the following methods:

**Build from source:**

1. Clone the backend repository:
```sh
❯ git clone https://github.com/gomemo-fmtpla/backend
```

2. Navigate to the project directory:
```sh
❯ cd backend
```

3. Install the project dependencies:


**Using `pip`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Pip-3776AB.svg?style={badge_style}&logo=pypi&logoColor=white" />](https://pypi.org/project/pip/)

```sh
❯ pip install -r requirements.txt
```


**Using `docker`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Docker-2CA5E0.svg?style={badge_style}&logo=docker&logoColor=white" />](https://www.docker.com/)

```sh
❯ docker build -t gomemo-fmtpla/backend .
```




###  Usage
Run backend using the following command:
**Using `pip`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Pip-3776AB.svg?style={badge_style}&logo=pypi&logoColor=white" />](https://pypi.org/project/pip/)

```sh
❯ python {entrypoint}
```


**Using `docker`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Docker-2CA5E0.svg?style={badge_style}&logo=docker&logoColor=white" />](https://www.docker.com/)

```sh
❯ docker run -it {image_name}
```


###  Testing
Run the test suite using the following command:
**Using `pip`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Pip-3776AB.svg?style={badge_style}&logo=pypi&logoColor=white" />](https://pypi.org/project/pip/)

```sh
❯ pytest
```


---
##  Project Roadmap

- [X] **`Task 1`**: <strike>Implement feature one.</strike>
- [ ] **`Task 2`**: Implement feature two.
- [ ] **`Task 3`**: Implement feature three.

---

##  Contributing

- **💬 [Join the Discussions](https://github.com/gomemo-fmtpla/backend/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/gomemo-fmtpla/backend/issues)**: Submit bugs found or log feature requests for the `backend` project.
- **💡 [Submit Pull Requests](https://github.com/gomemo-fmtpla/backend/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/gomemo-fmtpla/backend
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
   <a href="https://github.com{/gomemo-fmtpla/backend/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=gomemo-fmtpla/backend">
   </a>
</p>
</details>



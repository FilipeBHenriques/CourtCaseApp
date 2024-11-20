# CourtCaseApp


This project is a document processing application built with Flask and Python. The application processes HTML and JSON files, extracting information and storing it in an SQLite database. It also provides an API for interacting with the stored data.

## Design Choices

The application is built using **Flask** and **Python**, which were selected for the following reasons:

- **Flask**: Flask is a lightweight web framework that is easy to set up and extend. It provides simplicity, flexibility, and fine-grained control over the application’s structure. As an experienced Python developer, I found Flask to be a familiar choice, allowing me to quickly develop and deploy the application.
  
- **Python**: Python is used because of its wide adoption, rich ecosystem, and ease of use. The language’s extensive support for libraries and frameworks makes it ideal for quickly implementing features such as HTML and JSON parsing, database interaction, and web serving.

- **SQLite**: An SQLite database is used for storing the processed data due to its simplicity and ease of setup. It is lightweight, serverless, and doesn't require a dedicated database server, making it an ideal choice for this application where persistence and data structure are relatively simple.

## Caveats and Limitations

- **Performance**: Since the application uses SQLite, it is best suited for smaller-scale data processing tasks. If the application scales up in terms of the volume of data, it might require migrating to a more robust database system like PostgreSQL or MySQL.

- **Text Cleaning**: The text cleaning logic could be more robust, particularly in handling corner cases where the text structure might not be as expected. For example malformed data can be improved in future iterations of the application.

- **Docker Issue**: During development, I encountered an issue where Docker could not access the SQLite database file. This issue was persistent and I was unable to resolve it within the time constraints. The error message displayed was: `Docker sqlite3.OperationalError: unable to open database file`. It might be related to volume mounting or file permissions, but all my attempts failed to solve the issue.

## Potential Improvements

- **Better Text Parsing**: The text cleaning and processing could be improved, especially for edge cases involving HTML or JSON files with unexpected structures.
  
- **Database Migration**: While SQLite works for smaller projects, scaling this app to handle larger datasets might require migrating to a more performant database system such as PostgreSQL.

- **Error Handling**: The error handling around file parsing (HTML and JSON) could be more robust. Currently, if one file fails, it doesn't halt the entire process, but additional logging and better exception handling would be beneficial.

- **Docker Setup**: The Docker setup can be improved to ensure compatibility with database access, especially for local development environments. A more refined configuration might help solve issues like the one encountered during development.

## Command to Run the Docker Image

To run the Docker image, use the following command:

```bash
docker run -p 5000:5000 -v /path/to/data:/app/data <docker_image_name>

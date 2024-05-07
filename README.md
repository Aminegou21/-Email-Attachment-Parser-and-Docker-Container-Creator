
This project automates the process of extracting form data from PDF attachments in emails, parsing them to generate YAML configuration files, and subsequently deploying containerized databases based on the extracted data. It provides a seamless solution for handling PDF forms containing database connection details, enabling efficient setup and deployment of database instances.

Advantages:
1. **Streamlined Workflow**: Simplifies the process of setting up database instances by automating the extraction of configuration details from PDF forms.
2. **Enhanced Security**: Utilizes containerization for deploying databases, ensuring isolation and security of database instances.
3. **Dynamic Port Allocation**: Generates unique host ports for each container, preventing port conflicts and ensuring smooth deployment.
4. **Scalability**: Easily scalable to handle multiple PDF attachments concurrently, making it suitable for handling large volumes of form submissions.
5. **Customization**: Allows for customization of container environment variables based on the extracted form data, providing flexibility in configuration.

Usage:
1. Configure email credentials (`username` and `password`) in the script.
2. Run the script, which connects to the specified email server, fetches unread emails, and extracts attachments.
3. PDF attachments are parsed to extract database connection details and generate corresponding YAML configuration files.
4. Containerized databases are deployed using Docker based on the generated YAML configuration.
5. Users can access the deployed databases using the provided host ports.

This project is particularly useful for organizations or individuals dealing with a high volume of form submissions containing database connection information. It simplifies the setup process, improves efficiency, and enhances security by leveraging containerization technology.

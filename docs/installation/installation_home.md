# Installation

Welcome to the installation guide for Vane. Choose the installation method that best suits your needs:

## 1. Installation via Python Virtual Environment

Using Python virtual environments for application installation offers critical advantages in managing project dependencies and maintaining consistency across development workflows. Virtual environments allow for the isolation of project-specific dependencies, preventing conflicts between different projects and ensure that each project has access to the precise versions of libraries it requires.

This is the best option for most users and only requires Python (3.7-3.9 supported) to implement. For those who prefer using Python virtual environments, we have a detailed guide to help you set up your project environment using the traditional Python virtual environment approach.

[Explore the Python Virtual Environment installation method](python_installation.md)

## 2. Installation via Docker

Docker has many of same benefits as a Python Virtual Environment. Docker simplifies project management by encapsulating applications and dependencies in containers, ensuring consistency across diverse environments. Its lightweight nature enables efficient resource usage, while the ability to version and share Docker images facilitates collaboration and reproducibility. The [DockerFile](https://github.com/aristanetworks/vane/blob/develop/Dockerfile) for Vane
has been provided in the cloned repo.

However, Docker requires a Docker engine (like Docker Desktop) to implement. A Docker installations is best for integration into continuous integration and deployment pipelines, enhancing development workflows and productivity.

Simplify the installation process by using Docker containers. Our Docker guide provides instructions on how to quickly get started with our project in a containerized environment.

[Get started with Docker installation](docker_installation.md)

## 3. Installation via Poetry

Poetry also has many of same benefits as a Python Virtual Environment. Its straightforward configuration, comprehensive dependency resolution, and lock file system ensure consistent environments across different machines. Poetry streamlines the development process, making it easy to declare and manage project dependencies. It is the best route for contributing to Vane development.

However, this method requires the Python Poetry package for installation.

If you prefer managing your project dependencies with Poetry, follow our step-by-step guide on installing and setting up your environment using Poetry.

[Learn more about installing via Poetry](poetry_installation.md)

Choose the method that aligns with your workflow and dive into the respective section for detailed instructions.

# Costs management

This is the Back-End of an Expense Management System implemented in Python using the [`Flask`](https://flask.palletsprojects.com/en/3.0.x/) framework and [`MongoDB`](https://www.mongodb.com/) as the database.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)

## Overview

The Expense Management System Back-End is a RESTful API designed to handle expense management and categorization. It provides CRUD operations for managing expenses and their corresponding categories.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/emdhdri/costs-management.git
cd costs-management
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the flask application:

```bash
flask --app main run
```

or you can run it in debug mode:

```bash
flask --app main --debug run
```

The API will be accessible at http://127.0.0.1:5000.

## API Documentation

There is also a documentation for this api in doc directory. I've used [`apidoc`](https://apidocjs.com/) to create this documentation.

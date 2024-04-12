
# Face Recognition Sign-In/Sign-Out Application

This application uses face recognition to manage sign-ins and sign-outs. It is implemented in Python and uses AWS services, OpenCV (cv2), Tkinter for the GUI, Chalice for local development, Boto3 for AWS SDK, and Dlib for face recognition.

## Installation

1. Clone the repository.
2. Install the necessary packages mentioned in the `requirements.txt` file.

## Usage

1. Run the application locally using Chalice: `chalice local`.
2. The application GUI built with Tkinter will appear.
3. Use the "Sign In" and "Sign Out" buttons to manage user sessions.

## Features

- **Face Recognition**: The application uses Dlib's face recognition capabilities to identify users.
- **AWS Integration**: The application uses AWS services for storing user data and face embeddings. Boto3 is used as the AWS SDK.
- **Local Development**: The application can be run locally using Chalice.
- **GUI**: The application features a GUI built with Tkinter for easy usage.

## Contributing

Contributions are welcome. Please open an issue to discuss your ideas or initiate a Pull Request with your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

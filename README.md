# **🚀 FARM Skeleton (FastAPI + Next.js + MongoDB)**  

A minimal **FARM (FastAPI, React, MongoDB)** boilerplate with **JWT authentication** and **user CRUD** operations.  
Secure, scalable, and extendable for modern web applications.  

## **📌 Tech Stack**
- **Backend:** FastAPI, MongoDB, Motor, JWT, bcrypt
- **Frontend:** Next.js, Tailwind CSS, Axios, React Hook Form
- **Auth:** JSON Web Token (JWT) authentication  

---

# **📂 Project Structure**
```
farm-skeleton/
│── backend/             # FastAPI Backend
│   ├── app/
│   │   ├── models.py         # User models and validation
│   │   ├── database.py       # MongoDB connection setup
│   │   ├── main.py           # FastAPI entry point
│   │   ├── routes/
│   │   │   ├── users.py      # User CRUD operations
│   │   │   ├── auth.py       # Authentication routes
│   │   ├── security.py       # Password hashing & JWT handling
│   ├── .env                  # Environment variables
│   ├── requirements.txt      # Dependencies
│   ├── run.sh                # Startup script
│   ├── README.md             # Backend documentation
│
│── frontend/            # Next.js Frontend
│   ├── src/
│   │   ├── components/      # UI Components
│   │   ├── pages/
│   │   │   ├── index.js      # Home page
│   │   │   ├── login.js      # Login page
│   │   │   ├── register.js   # Register page
│   │   │   ├── profile.js    # User profile (protected)
│   │   ├── utils/
│   │   │   ├── api.js        # API request handler
│   │   │   ├── auth.js       # JWT auth utilities
│   ├── .env.local             # Environment variables
│   ├── package.json          # Frontend dependencies
│   ├── README.md             # Frontend documentation
│
│── README.md             # Overall project documentation
```

---

## **🔧 Setup Instructions**  

### **🖥 Backend Setup (FastAPI)**
1️⃣ **Navigate to the backend folder**
```sh
cd backend
```

2️⃣ **Create a virtual environment**
```sh
python -m venv venv
source venv/bin/activate  # On Mac/Linux
venv\Scripts\activate     # On Windows
```

3️⃣ **Install dependencies**
```sh
pip install -r requirements.txt
```

4️⃣ **Set up environment variables**  
Create a `.env` file:
```
MONGO_URI=mongodb://localhost:27017/farm_skeleton
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5️⃣ **Run the server**
```sh
chmod +x run.sh
./run.sh
```
or manually:
```sh
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### **🌐 Frontend Setup (Next.js)**
1️⃣ **Navigate to the frontend folder**
```sh
cd frontend
```

2️⃣ **Install dependencies**
```sh
npm install
```

3️⃣ **Set up environment variables**  
Create a `.env.local` file:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

4️⃣ **Run the frontend**
```sh
npm run dev
```

---

## **🛠 API Endpoints**
### **User CRUD**
| Operation     | API Route            | Method |
|--------------|---------------------|--------|
| Create User  | `/api/users`        | `POST` |
| List Users   | `/api/users`        | `GET`  |
| Get User     | `/api/users/{id}`   | `GET`  |
| Update User  | `/api/users/{id}`   | `PUT`  |
| Delete User  | `/api/users/{id}`   | `DELETE` |

### **Authentication**
| Operation    | API Route            | Method |
|-------------|---------------------|--------|
| Sign-in     | `/auth/signin`       | `POST` |

---

## **🔍 Testing the API**
### 1️⃣ **Test with cURL**
Sign in:
```sh
curl -X POST "http://localhost:8000/auth/signin" -H "Content-Type: application/json" -d '{"email": "test@example.com", "password": "yourpassword"}'
```

### 2️⃣ **Test with Postman**
- Import the API routes  
- Send `POST`, `GET`, `PUT`, `DELETE` requests  

---

## **✅ Next Steps**
🚀 **Enhancements & Features to Add**  
- 🔹 **User Roles** (Admin, Normal User)  
- 🔹 **Email Verification**  
- 🔹 **Frontend UI with Tailwind Components**  
- 🔹 **Unit Testing & Documentation**  
- 🔹 **Deploy to Vercel (Frontend) & Render (Backend)**  

---

## **💡 Contributing**
Pull requests are welcome! Feel free to open an issue to suggest improvements.  

---

## **📜 License**
This project is open-source under the **MIT License**.  

---

🚀 **Happy Coding!** 🚀
import React from "react";

const LoginForm = ({ setIsLoginOpen }) => {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
      {/* Form đăng nhập */}
      <div className="bg-white p-6 rounded-lg shadow-lg w-96 relative">
        {/* Nút đóng popup nằm trong form */}
        <button
          className="absolute top-3 right-3 text-gray-500 hover:text-black text-lg"
          onClick={() => setIsLoginOpen(false)}
        >
          ✖
        </button>

        <h2 className="text-xl font-semibold text-center mb-4">Đăng nhập</h2>

        {/* Input tài khoản */}
        <input
          type="text"
          placeholder="Tài khoản"
          className="w-full p-2 mb-3 border border-gray-300 rounded-md"
        />

        {/* Input mật khẩu */}
        <input
          type="password"
          placeholder="Mật khẩu"
          className="w-full p-2 mb-3 border border-gray-300 rounded-md"
        />

        {/* Nút đăng nhập */}
        <button className="w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 transition">
          Đăng nhập
        </button>
      </div>
    </div>
  );
};

export default LoginForm;

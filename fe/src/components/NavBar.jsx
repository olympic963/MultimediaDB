import React from 'react';

const NavBar = ({ setIsLoginOpen }) => {
  return (
    <div className="fixed top-0 left-0 w-full h-[5%] flex items-center px-4" style={{ backgroundColor: "rgb(51,51,51)" }}>
      {/* <button className="ml-auto bg-white text-black px-2 py-1 rounded-md shadow-md hover:bg-gray-200 transition"  onClick={() => setIsLoginOpen(true)}>
        Đăng nhập
      </button> */}
    </div>
  );
}

export default NavBar;

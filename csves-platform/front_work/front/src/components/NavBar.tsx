import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";

type UserRole = "user" | "admin";

const NavBar: React.FC = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const userRole: UserRole = "user"; // 或 "admin"
  const navigate = useNavigate();
  const menuRef = useRef<HTMLDivElement>(null);

  // ✅ 点击外部区域自动关闭菜单
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <nav className="fixed top-0 left-0 w-full z-50 bg-gradient-to-r from-purple-300 via-purple-100 to-purple-300 text-white px-3 py-1 flex justify-between items-center shadow-md backdrop-blur">
      <div className="flex items-center gap-2 text-base font-semibold tracking-wide">
        <img
          src="/logo.png"
          alt="系统 Logo"
          className="w-8 h-8 rounded-full bg-white object-contain"
        />
        <span> MagicChart</span>
      </div>

      <div className="relative" ref={menuRef}>
        {/* 用户头像 */}
        <img
          src="https://i.pravatar.cc"
          alt="User Avatar"
          className="w-7 h-7 rounded-full border border-white cursor-pointer hover:scale-105 transition-transform"
          onClick={() => setMenuOpen((prev) => !prev)}
        />

        {/* 下拉菜单 */}
        {menuOpen && (
          <div className="absolute right-0 mt-1 w-40 bg-white text-black rounded-xl shadow-lg z-50 py-2">
            {userRole === "user" ? (
              <>
                <div
                  onClick={() => {
                    navigate("/setting");
                    setMenuOpen(false);
                  }}
                  className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                >
                  个人设置
                </div>
                <div
                  onClick={() => {
                    navigate("/history");
                    setMenuOpen(false);
                  }}
                  className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                >
                  历史记录
                </div>
              </>
            ) : (
              <>
                <div
                  onClick={() => {
                    navigate("/templatesmanagement");
                    setMenuOpen(false);
                  }}
                  className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                >
                  模板管理
                </div>
                <div
                  onClick={() => {
                    navigate("/usermanagement");
                    setMenuOpen(false);
                  }}
                  className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                >
                  用户管理
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  );
};

export default NavBar;

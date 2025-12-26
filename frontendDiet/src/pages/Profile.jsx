import React from "react";
import { useNavigate } from "react-router-dom";
import { FaFire, FaBell, FaUser } from "react-icons/fa";
import { CgGym } from "react-icons/cg";

const Profile = () => {
  const navigate = useNavigate();

  const menuItems = [
    {
      title: "Daily Calorie Goal",
      subtitle: "2,000 Calories",
      icon: <FaFire className="text-orange-500 text-2xl" />,
      route: "/nutrition"
    },
    {
      title: "Macro Targets",
      subtitle: "Carbs: 50% · Protein: 25% · Fat: 25%",
      icon: <CgGym className="text-blue-500 text-2xl" />,
      route: "/nutrition"
    },
    {
      title: "Personal Information",
      subtitle: "",
      icon: <FaUser className="text-yellow-500 text-2xl" />,
      route: "/profile/edit"
    },
    {
      title: "Notifications",
      subtitle: "",
      icon: <FaBell className="text-blue-500 text-2xl" />,
      route: "/settings"
    },
  ];

  return (
    <div className="px-6 py-8">
      <h2 className="text-3xl font-bold text-center mb-8 text-gray-800">Profile</h2>

      {/* Profile Card */}
      <div className="bg-white rounded-2xl shadow p-5 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <img
            src="https://via.placeholder.com/80"
            alt="User Avatar"
            className="w-16 h-16 rounded-full"
          />
          <div>
            <h3 className="text-xl font-semibold text-gray-800">John Doe</h3>
            <p className="text-gray-500 text-sm">johndoe@email.com</p>
          </div>
        </div>
        <button className="bg-blue-100 text-blue-600 px-4 py-1 rounded-lg text-sm">
          Edit
        </button>
      </div>

      {/* Menu List */}
      <div className="mt-6 space-y-4">
        {menuItems.map((item, index) => (
          <button
            key={index}
            onClick={() => navigate(item.route)}
            className="w-full bg-white rounded-2xl shadow p-4 flex items-center justify-between"
          >
            <div className="flex items-center gap-4">
              {item.icon}
              <div className="text-left">
                <p className="font-semibold text-gray-800">{item.title}</p>
                {item.subtitle && (
                  <p className="text-gray-500 text-sm">{item.subtitle}</p>
                )}
              </div>
            </div>

            <span className="text-gray-400 text-xl">›</span>
          </button>
        ))}
      </div>

      {/* Log Out Button */}
      <button
        className="mt-10 w-full bg-red-500 hover:bg-red-600 text-white font-semibold py-3 rounded-2xl shadow"
        onClick={() => navigate("/")}
      >
        Log Out
      </button>
    </div>
  );
};

export default Profile;
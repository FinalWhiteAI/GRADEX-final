import React from "react";
import { useNavigate } from "react-router-dom";
import { BookOpen, Notebook, Brain, Settings } from "lucide-react";

export default function OurAppPage() {
  const navigate = useNavigate();

  const cards = [
    {
      id: 1,
      title: "Classroom",
      desc: "Manage classes, assignments & submissions",
      icon: <BookOpen size={32} />,
      route: "/login",
    },
    {
      id: 2,
      title: "Notebook AI",
      desc: "Smart notes, organize & access anywhere",
      icon: <Notebook size={32} />,
      route: "https://wqlq1078-5174.inc1.devtunnels.ms/",
    },
    {
      id: 3,
      title: "forms",
      desc: "Create, attempt & review quiz challenges",
      icon: <Brain size={32} />,
      route: "https://m6hd3lmp-5174.inc1.devtunnels.ms/",
    },
    {
      id: 4,
      title: "Respone",
      desc: "Customize preferences & account",
      icon: <Settings size={32} />,
      route: "https://m6hd3lmp-5173.inc1.devtunnels.ms/",
    },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white px-6 py-10">
      <h1 className="text-3xl font-bold mb-8 text-center">Welcome 👋</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-4xl mx-auto">
        {cards.map((card) => (
          <div
            key={card.id}
            onClick={() => {
  if (card.route.startsWith("http")) {
    window.open(card.route, "_blank"); // external link
  } else {
    navigate(card.route); // internal route
  }
}}
            className="cursor-pointer bg-gray-800 rounded-xl border border-gray-700 p-6 
                       flex flex-col items-start gap-3 hover:bg-gray-750 
                       hover:-translate-y-1 hover:shadow-xl hover:border-blue-500 
                       transition-all duration-300"
          >
            <div className="text-blue-400">{card.icon}</div>
            <h2 className="text-xl font-semibold">{card.title}</h2>
            <p className="text-gray-400 text-sm">{card.desc}</p>
          </div>
        ))}
      </div>
<button
  onClick={() => navigate("/login")}
  className="mt-10 mx-auto block px-6 py-3 bg-blue-600 hover:bg-blue-700 
             text-white font-semibold rounded-xl shadow-lg 
             transition-all duration-300 hover:shadow-blue-500/30"
>
  Get Started
</button>
    </div>
  );
}

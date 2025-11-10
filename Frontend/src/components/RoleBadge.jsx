export default function RoleBadge({ roles }) {
  // roles can be array or string
  const list = Array.isArray(roles) ? roles : (roles ? JSON.parse(roles || "[]") : []);
  return (
    <div className="flex gap-2">
      {list.map((r) => (
        <span key={r} className="text-xs px-2 py-1 rounded-full bg-gray-100 border text-gray-700">
          {r.replace(/_/g, " ")}
        </span>
      ))}
    </div>
  );
}

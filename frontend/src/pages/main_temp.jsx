import { Outlet, Link } from "react-router-dom";

export default function Maintemp() {
  return (
    <div className="bg-gray-900 text-white min-h-screen">
      <nav className="shadow-md">
        <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
          <div className="text-xl font-bold tracking-wide">Lenseshot</div>

          <div className="space-x-6">
            <Link to="/" className="hover:text-gray-300">
              Home
            </Link>
            <Link to="/projects" className="hover:text-gray-300">
              Projects
            </Link>
            <Link to="/contacts" className="hover:text-gray-300">
              Contacts
            </Link>
            <Link to="/account" className="hover:text-gray-300">
              Account
            </Link>
          </div>
        </div>
      </nav>

      <main className="p-4">
        <Outlet />
      </main>
    </div>
  );
}

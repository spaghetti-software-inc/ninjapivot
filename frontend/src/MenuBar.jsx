import React from 'react';

function MenuBar() {
  return (
    <nav className="bg-purple-900 p-4 fixed w-full top-0 z-10">
      <ul className="flex flex-nowrap space-x-4">
        <li>
          <a href="#home" className="w-auto whitespace-nowrap text-white hover:bg-purple-700 px-3 py-2 rounded">
            Dashboard
          </a>
        </li>
        <li className="relative group">
          <a href="#reports" className="w-auto whitespace-nowrap text-white hover:bg-purple-700 px-3 py-2 rounded">
            Reports
          </a>
          <div className="absolute hidden group-hover:block bg-purple-800 text-white mt-1 rounded shadow-lg">
            <a href="#report1" className="block w-auto whitespace-nowrap px-4 py-2 hover:bg-purple-700">
              Report 1
            </a>
            <a href="#report2" className="block w-auto whitespace-nowrap px-4 py-2 hover:bg-purple-700">
              Report 2
            </a>
          </div>
        </li>
        <li className="relative group">
          <a href="#data" className="w-auto whitespace-nowrap text-white hover:bg-purple-700 px-3 py-2 rounded">
            Data
          </a>
          <div className="absolute hidden group-hover:block bg-purple-800 text-white mt-1 rounded shadow-lg">
            <a href="#dataentry" className="block w-auto whitespace-nowrap px-4 py-2 hover:bg-purple-700">
              Data Entry
            </a>
            <a href="#database" className="block w-auto whitespace-nowrap px-4 py-2 hover:bg-purple-700">
              Database
            </a>
          </div>
        </li>
        <li>
          <a href="#risk" className="w-auto whitespace-nowrap text-white hover:bg-purple-700 px-3 py-2 rounded">
            Risk
          </a>
        </li>
      </ul>
    </nav>
  );
}

export default MenuBar;

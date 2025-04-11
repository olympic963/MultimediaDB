import { useState } from "react";
import { FaSearch } from "react-icons/fa";

const SearchBar = () => {
    const [file, setFile] = useState(null);

    const handleFileChange = (event) => {
        const selectedFile = event.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
        }
    };

    return (
        <div className="flex items-center bg-white border border-gray-200 rounded-full shadow-md px-3 py-2 w-[50%] space-x-2 py-4">
            <FaSearch />

            <textarea
                className="resize-none overflow-hidden bg-transparent outline-none h-full flex-1"
                placeholder="Tìm metadata"
                rows="1"
                onKeyDown={(e) => {
                    if (e.key === "Enter") e.preventDefault();
                }}
            />

            <input
                type="file"
                accept="audio/*"
                id="audio-upload"
                className="h-full text-sm text-blue-500 appearance-none"
                onChange={handleFileChange}
            />
        </div>
    );
};

export default SearchBar;

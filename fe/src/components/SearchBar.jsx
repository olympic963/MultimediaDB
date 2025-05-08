import { useState } from "react";
import { FaSearch } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

const SearchBar = ({ setIsLoading, setError }) => {
    const navigate = useNavigate();
    const [keyword, setKeyword] = useState("");

    const sendSearchRequest = async (formData) => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await fetch("http://localhost:8000/api/search", {
                method: "POST",
                body: formData
            });
            
            if (!response.ok) {
                console.error("Search request failed:", response.statusText);
                throw new Error("Search request failed");
            }
            
            const data = await response.json();
            console.log("Search response:", data);
            navigate(`/results?query_id=${data.query_id}`);
        } catch (error) {
            console.error("Error sending search request:", error);
            setError("Không thể kết nối đến server. Vui lòng thử lại sau.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileChange = (event) => {
        const selectedFile = event.target.files[0];
        if (selectedFile) {
            const formData = new FormData();
            formData.append("file", selectedFile);
            sendSearchRequest(formData);
        }
    };

    const handleKeywordChange = (event) => {
        setKeyword(event.target.value);
    };

    const handleKeyDown = (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            if (keyword.trim() !== "") {
                const formData = new FormData();
                formData.append("keyword", keyword.trim());
                sendSearchRequest(formData);
            }
        }
    };

    return (
        <div className="flex items-center bg-white border border-gray-200 rounded-full shadow-md px-3 py-2 w-[50%] space-x-2 py-4">
            <FaSearch />
            <textarea
                className="resize-none overflow-hidden bg-transparent outline-none h-full flex-1"
                placeholder="Tìm metadata"
                rows="1"
                value={keyword}
                onChange={handleKeywordChange}
                onKeyDown={handleKeyDown}
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

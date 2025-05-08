import React, { useEffect, useState } from 'react';
import SearchBar from './SearchBar';
import Logo from '../assets/Logo2.png';
import NavBar from './NavBar';
import Loading from './Loading';
import { useSearchParams, Link } from 'react-router-dom';

const ResultPage = () => {
  const [searchParams] = useSearchParams();
  const queryId = searchParams.get('query_id');
  const [searchResults, setSearchResults] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchResults = async () => {
      if (!queryId) {
        setError('Không tìm thấy ID tìm kiếm. Vui lòng thực hiện tìm kiếm trước.');
        setIsLoading(false);
        return;
      }

      try {
        const response = await fetch(`http://localhost:8000/api/search/result/${queryId}`);
        if (!response.ok) {
          throw new Error('Không thể lấy kết quả tìm kiếm. Vui lòng thử lại sau.');
        }
        const data = await response.json();
        setSearchResults(data);
      } catch (err) {
        console.error('Error fetching results:', err);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchResults();
  }, [queryId]);

  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-gray-50 to-gray-100">
      <NavBar />
      <div className="fixed top-11 left-0 right-0 bg-white shadow-lg z-40">
        <div className="w-full px-6 py-3">
          <div className="flex items-center gap-4">
            <Link to="/">
              <img src={Logo} alt="Logo2" className="h-12 w-auto cursor-pointer" />
            </Link>
            <SearchBar setIsLoading={setIsLoading} setError={setError} />
          </div>
        </div>
      </div>
      <div className="pt-40 px-6 pb-10">
        {isLoading ? (
          <div className="flex justify-center items-center h-40">
            <Loading />
          </div>
        ) : error ? (
          <div className="flex justify-center w-full">
            <div className="text-red-500 bg-red-50 px-4 py-2 rounded-lg border border-red-200 max-w-md w-full text-center">
              {error}
            </div>
          </div>
        ) : searchResults ? (
          <div className="space-y-8">
            <div className="w-full flex flex-col items-center gap-8">
              {searchResults.temp_file_name && (
                <div className="bg-white rounded-xl shadow-lg p-6 w-4/5">
                  <h2 className="text-2xl font-bold mb-6 text-gray-800">
                    File đã tải lên
                  </h2>
                  <div className="aspect-w-16 aspect-h-9">
                    <audio
                      controls
                      className="w-full"
                      src={`http://localhost:8000/api/stream/${searchResults.temp_file_name}?type=temp`}
                    >
                      Your browser does not support the audio element.
                    </audio>
                  </div>
                </div>
              )}
              <div className="bg-white rounded-xl shadow-lg p-6 w-4/5">
                <h2 className="text-2xl font-bold mb-6 text-gray-800">
                  Kết quả tìm kiếm
                </h2>
                <div className="space-y-6">
                  {searchResults.results.map((result, index) => (
                    <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold">{result.file_name}</h3>
                        <span className="text-indigo-600 font-medium">
                          {(result.similarity * 100).toFixed(2)}% tương đồng
                        </span>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                        <div>
                          <span className="font-medium">Định dạng:</span> {result.file_type}
                        </div>
                        <div>
                          <span className="font-medium">Kích thước:</span> {result.file_size_kb.toFixed(2)} KB
                        </div>
                        <div>
                          <span className="font-medium">Tần số:</span> {result.sample_rate} Hz
                        </div>
                        <div>
                          <span className="font-medium">Thời lượng:</span> {result.duration.toFixed(2)}s
                        </div>
                      </div>
                      <div className="mt-4">
                        <audio
                          controls
                          className="w-full"
                          src={`http://localhost:8000/api/stream/${result.file_name}?type=result`}
                        >
                          Your browser does not support the audio element.
                        </audio>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};

export default ResultPage;
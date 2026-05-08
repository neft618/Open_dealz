import React, { useState } from 'react';

const FileUpload = ({ onFileSelect, accept = '*', multiple = false }) => {
  const [files, setFiles] = useState([]);

  const handleChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
    onFileSelect(selectedFiles);
  };

  return (
    <div className="border-2 border-dashed border-gray-300 rounded p-4 text-center">
      <input
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={handleChange}
        className="hidden"
        id="file-upload"
      />
      <label htmlFor="file-upload" className="cursor-pointer text-blue-600 hover:text-blue-800">
        Click to upload or drag and drop
      </label>
      {files.length > 0 && (
        <ul className="mt-2">
          {files.map((file, index) => (
            <li key={index} className="text-sm text-gray-600">{file.name}</li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default FileUpload;
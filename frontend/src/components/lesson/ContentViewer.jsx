import { useState, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';

// Configure PDF.js worker - Using CDN
pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

function ContentViewer({ lesson }) {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [pageWidth, setPageWidth] = useState(null);
  const [contentUrl, setContentUrl] = useState(null);

  // Build authenticated content URL
  useEffect(() => {
    if (lesson.content_url) {
      const url = `/api/lessons/${lesson.id}/content`;
      setContentUrl(url);
    }
  }, [lesson.content_url, lesson.id]);

  // Set PDF width based on container
  useEffect(() => {
    const updateWidth = () => {
      const container = document.getElementById('pdf-container');
      if (container) {
        // Use 95% of container width for some padding
        setPageWidth(container.offsetWidth * 0.95);
      }
    };

    updateWidth();
    window.addEventListener('resize', updateWidth);
    return () => window.removeEventListener('resize', updateWidth);
  }, []);

  const fileName = lesson.content_url?.split('/').pop() || '';
  const fileExtension = fileName.toLowerCase().split('.').pop();

  // PDF Document Success Handler
  function onDocumentLoadSuccess({ numPages }) {
    setNumPages(numPages);
    setPageNumber(1);
  }

  // Change PDF page
  function changePage(offset) {
    setPageNumber(prevPageNumber => {
      const newPage = prevPageNumber + offset;
      // Ensure page is within bounds
      if (newPage >= 1 && newPage <= numPages) {
        return newPage;
      }
      return prevPageNumber;
    });
  }

  function previousPage() {
    changePage(-1);
  }

  function nextPage() {
    changePage(1);
  }

  function goToPage(page) {
    if (page >= 1 && page <= numPages) {
      setPageNumber(page);
    }
  }

  // Check if no content
  if (!lesson.content_url) {
    return (
      <div className="bg-gray-50 rounded-lg p-12 text-center border-2 border-dashed border-gray-300">
        <div className="text-6xl mb-4">📄</div>
        <h3 className="text-xl font-semibold text-gray-700 mb-2">
          No content available yet
        </h3>
        <p className="text-gray-500">
          The instructor hasn't uploaded content for this lesson
        </p>
      </div>
    );
  }

  // PDF Files - Using react-pdf
  if (fileExtension === 'pdf') {
    return (
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden mb-6">
        {/* PDF Controls */}
        <div className="bg-gray-800 text-white px-4 py-3 flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center space-x-3">
            <button
              onClick={previousPage}
              disabled={pageNumber <= 1}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              ← Previous
            </button>
            
            <div className="flex items-center space-x-2">
              <span className="text-sm">Page</span>
              <input
                type="number"
                min="1"
                max={numPages || 1}
                value={pageNumber}
                onChange={(e) => {
                  const page = parseInt(e.target.value);
                  if (!isNaN(page)) {
                    goToPage(page);
                  }
                }}
                className="w-16 px-2 py-1 bg-gray-700 border border-gray-600 rounded text-center text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-sm">of {numPages || '...'}</span>
            </div>

            <button
              onClick={nextPage}
              disabled={pageNumber >= numPages}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              Next →
            </button>
          </div>

          <div className="text-sm text-gray-300">
            📄 {fileName}
          </div>
        </div>

        {/* PDF Viewer */}
        <div 
          id="pdf-container"
          className="overflow-auto bg-gray-100 flex justify-center py-6"
          style={{ maxHeight: '80vh' }}
        >
          <Document
            file={{
              url: contentUrl,
              httpHeaders: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
              }
            }}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={(error) => {
              console.error('Error loading PDF:', error);
            }}
            loading={
              <div className="text-center py-20">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                <p className="text-gray-600 font-medium">Loading PDF...</p>
              </div>
            }
            error={
              <div className="text-center py-20">
                <div className="text-5xl mb-4 text-red-600">⚠️</div>
                <p className="text-red-600 font-semibold mb-2">Failed to load PDF</p>
                <p className="text-gray-600 text-sm">Please try refreshing the page</p>
              </div>
            }
          >
            <Page
              pageNumber={pageNumber}
              width={pageWidth}
              renderTextLayer={true}
              renderAnnotationLayer={true}
              className="shadow-lg"
            />
          </Document>
        </div>

        {/* Page Navigation Helper */}
        {numPages > 1 && (
          <div className="bg-gray-50 border-t border-gray-200 px-4 py-3 flex items-center justify-center space-x-2">
            <button
              onClick={() => goToPage(1)}
              disabled={pageNumber === 1}
              className="px-3 py-1 bg-white border border-gray-300 rounded text-sm hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              First
            </button>
            <button
              onClick={previousPage}
              disabled={pageNumber <= 1}
              className="px-3 py-1 bg-white border border-gray-300 rounded text-sm hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              ← Prev
            </button>
            <span className="text-sm text-gray-600 px-3">
              {pageNumber} / {numPages}
            </span>
            <button
              onClick={nextPage}
              disabled={pageNumber >= numPages}
              className="px-3 py-1 bg-white border border-gray-300 rounded text-sm hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next →
            </button>
            <button
              onClick={() => goToPage(numPages)}
              disabled={pageNumber === numPages}
              className="px-3 py-1 bg-white border border-gray-300 rounded text-sm hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Last
            </button>
          </div>
        )}
      </div>
    );
  }

  // Video Files - HTML5 Player
  if (['mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv'].includes(fileExtension)) {
    return (
      <div className="bg-black rounded-lg overflow-hidden mb-6">
        <video
          controls
          controlsList="nodownload"
          className="w-full"
          style={{ maxHeight: '70vh' }}
          preload="metadata"
        >
          <source src={contentUrl} type={`video/${fileExtension === 'mov' ? 'quicktime' : fileExtension}`} />
          Your browser does not support the video tag.
        </video>
        <div className="bg-gray-900 px-4 py-2 text-xs text-gray-400">
          🎥 {fileName}
        </div>
      </div>
    );
  }

  // Office Documents - Google Docs Viewer
  if (['doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'].includes(fileExtension)) {
    const publicUrl = window.location.origin + contentUrl;
    
    return (
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden mb-6">
        <div className="bg-blue-50 border-b border-blue-200 px-4 py-3 flex items-center justify-between">
          <p className="text-sm text-blue-800 flex items-center">
            <span className="mr-2">ℹ️</span>
            Viewing {fileExtension.toUpperCase()} document
          </p>
          <span className="text-xs text-blue-600">📄 {fileName}</span>
        </div>
        <iframe
          src={`https://docs.google.com/viewer?url=${encodeURIComponent(publicUrl)}&embedded=true`}
          className="w-full border-0"
          style={{ height: '80vh' }}
          title={lesson.title}
        />
      </div>
    );
  }

  // Text Files - Display inline
  if (['txt', 'md'].includes(fileExtension)) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden mb-6">
        <div className="bg-gray-100 border-b border-gray-200 px-4 py-3">
          <p className="text-sm text-gray-700 font-medium">📝 {fileName}</p>
        </div>
        <iframe
          src={contentUrl}
          className="w-full border-0 bg-white"
          style={{ height: '70vh' }}
          title={lesson.title}
          sandbox="allow-same-origin"
        />
      </div>
    );
  }

  // Fallback - Download option for unsupported types
  return (
    <div className="bg-gray-50 rounded-lg p-12 text-center border border-gray-200 mb-6">
      <div className="text-6xl mb-4">📦</div>
      <h3 className="text-xl font-semibold text-gray-700 mb-2">
        {fileName}
      </h3>
      <p className="text-gray-600 mb-2">
        File type: <span className="font-mono text-sm bg-gray-200 px-2 py-1 rounded">{fileExtension}</span>
      </p>
      <p className="text-gray-500 mb-6">
        This file type cannot be previewed in the browser
      </p>
      <a
      
        href={contentUrl}
        download
        className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
      >
        📥 Download to View
      </a>
    </div>
  );
}

export default ContentViewer;
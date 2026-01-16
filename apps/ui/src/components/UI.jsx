import React from 'react';

export const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md',
  className = '',
  disabled = false,
  ...props 
}) => {
  const baseStyles = 'font-semibold rounded-lg transition-colors duration-200 flex items-center justify-center gap-2';
  
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-400',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 disabled:bg-gray-300',
    danger: 'bg-red-600 text-white hover:bg-red-700 disabled:bg-gray-400',
    success: 'bg-green-600 text-white hover:bg-green-700 disabled:bg-gray-400',
    outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50 disabled:border-gray-400 disabled:text-gray-400',
  };

  const sizes = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};

export const Card = ({ children, className = '', title = null, ...props }) => (
  <div className={`bg-white rounded-lg shadow-md p-6 ${className}`} {...props}>
    {title && <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>}
    {children}
  </div>
);

export const Modal = ({ isOpen, onClose, title, children, size = 'md' }) => {
  if (!isOpen) return null;

  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className={`bg-white rounded-lg shadow-xl ${sizes[size]} w-full max-h-[90vh] overflow-y-auto`}>
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl leading-none"
          >
            ×
          </button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
};

export const Input = ({ 
  label, 
  error = null, 
  className = '',
  type = 'text',
  ...props 
}) => (
  <div className="w-full">
    {label && <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>}
    <input
      type={type}
      className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
        error ? 'border-red-500' : 'border-gray-300'
      } ${className}`}
      {...props}
    />
    {error && <p className="text-red-600 text-sm mt-1">{error}</p>}
  </div>
);

export const Select = ({ 
  label, 
  options = [], 
  error = null,
  className = '',
  ...props 
}) => (
  <div className="w-full">
    {label && <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>}
    <select
      className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
        error ? 'border-red-500' : 'border-gray-300'
      } ${className}`}
      {...props}
    >
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
    {error && <p className="text-red-600 text-sm mt-1">{error}</p>}
  </div>
);

export const Badge = ({ children, variant = 'blue', className = '' }) => {
  const variants = {
    blue: 'bg-blue-100 text-blue-800',
    green: 'bg-green-100 text-green-800',
    red: 'bg-red-100 text-red-800',
    yellow: 'bg-yellow-100 text-yellow-800',
    gray: 'bg-gray-100 text-gray-800',
  };

  return (
    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
};

export const Table = ({ headers, rows, actions = null, className = '' }) => (
  <div className={`overflow-x-auto ${className}`}>
    <table className="min-w-full border-collapse">
      <thead>
        <tr className="bg-gray-100 border-b border-gray-300">
          {headers.map((header) => (
            <th key={header} className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
              {header}
            </th>
          ))}
          {actions && <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Actions</th>}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, idx) => (
          <tr key={idx} className="border-b border-gray-200 hover:bg-gray-50">
            {Object.values(row).map((cell, cellIdx) => (
              <td key={cellIdx} className="px-6 py-3 text-sm text-gray-700">
                {cell}
              </td>
            ))}
            {actions && (
              <td className="px-6 py-3 text-sm flex gap-2">
                {actions(row)}
              </td>
            )}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

export const LoadingSpinner = ({ size = 'md', className = '' }) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className={`inline-flex items-center justify-center ${className}`}>
      <div className={`${sizes[size]} border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin`}></div>
    </div>
  );
};

export const Alert = ({ type = 'info', message, onClose = null }) => {
  const types = {
    info: 'bg-blue-50 text-blue-800 border-blue-200',
    success: 'bg-green-50 text-green-800 border-green-200',
    error: 'bg-red-50 text-red-800 border-red-200',
    warning: 'bg-yellow-50 text-yellow-800 border-yellow-200',
  };

  return (
    <div className={`border rounded-lg p-4 ${types[type]} flex items-center justify-between`}>
      <span>{message}</span>
      {onClose && (
        <button onClick={onClose} className="text-lg font-bold cursor-pointer">
          ×
        </button>
      )}
    </div>
  );
};

export const Pagination = ({ currentPage, totalPages, onPageChange }) => (
  <div className="flex items-center gap-2 mt-4">
    <Button
      variant="outline"
      size="sm"
      disabled={currentPage === 1}
      onClick={() => onPageChange(currentPage - 1)}
    >
      Previous
    </Button>
    <span className="text-sm text-gray-600">
      Page {currentPage} of {totalPages}
    </span>
    <Button
      variant="outline"
      size="sm"
      disabled={currentPage === totalPages}
      onClick={() => onPageChange(currentPage + 1)}
    >
      Next
    </Button>
  </div>
);

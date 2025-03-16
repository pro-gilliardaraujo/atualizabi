'use client';

import { useState } from 'react';

const reportTypes = [
  { 
    id: 'plantio',
    name: 'Plantio',
    pages: [
      { id: 'frente1', name: 'Frente 1' }
    ]
  },
  {
    id: 'colheita',
    name: 'Colheita',
    pages: [
      { id: 'arakaki', name: 'Arakaki' },
      { id: 'ituiutaba', name: 'Ituiutaba' },
      { id: 'iturama', name: 'Iturama' },
      { id: 'ouroeste', name: 'Ouroeste' },
      { id: 'zirleno', name: 'Zirleno' }
    ]
  },
  {
    id: 'cav',
    name: 'CAV',
    pages: [
      { id: 'frente1', name: 'Frente 1' },
      { id: 'frente2', name: 'Frente 2' },
      { id: 'frente3', name: 'Frente 3' },
      { id: 'frente4', name: 'Frente 4' }
    ]
  },
  {
    id: 'bonificacoes',
    name: 'Bonificações',
    pages: [
      { id: 'geral', name: 'Geral' },
      { id: 'individual', name: 'Individual' }
    ]
  }
];

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedPage, setSelectedPage] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !selectedCategory || !selectedPage) {
      setMessage('Por favor, selecione um arquivo, categoria e página');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', selectedCategory);
    formData.append('page', selectedPage);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setMessage(data.message);
    } catch (error) {
      setMessage('Erro ao enviar arquivo. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const selectedCategoryPages = reportTypes.find(cat => cat.id === selectedCategory)?.pages || [];

  return (
    <main className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold mb-8 text-center text-gray-800">Atualização de Relatórios</h1>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-2">
              Categoria
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => {
                setSelectedCategory(e.target.value);
                setSelectedPage('');
              }}
              className="w-full p-2 border border-gray-400 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-blue-600 bg-white text-gray-800"
            >
              <option value="">Selecione uma categoria</option>
              {reportTypes.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>

          {selectedCategory && (
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-2">
                Página
              </label>
              <select
                value={selectedPage}
                onChange={(e) => setSelectedPage(e.target.value)}
                className="w-full p-2 border border-gray-400 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-blue-600 bg-white text-gray-800"
              >
                <option value="">Selecione uma página</option>
                {selectedCategoryPages.map((page) => (
                  <option key={page.id} value={page.id}>
                    {page.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-2">
              Arquivo Excel
            </label>
            <input
              type="file"
              accept=".xlsx,.xls"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="w-full p-2 border border-gray-400 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-blue-600 bg-white text-gray-800 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3 px-4 rounded-md text-white font-semibold text-lg 
              ${loading 
                ? 'bg-gray-500 cursor-not-allowed' 
                : 'bg-blue-700 hover:bg-blue-800 active:bg-blue-900'}`}
          >
            {loading ? 'Enviando...' : 'Enviar Arquivo'}
          </button>
        </form>

        {message && (
          <div className={`mt-6 p-4 rounded-md text-base font-medium ${
            message.includes('Erro') 
              ? 'bg-red-100 text-red-800 border border-red-300' 
              : 'bg-green-100 text-green-800 border border-green-300'
          }`}>
            {message}
          </div>
        )}
      </div>
    </main>
  );
}

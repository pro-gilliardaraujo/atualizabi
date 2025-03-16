'use client';

import { useState } from 'react';

const reportTypes = [
  { id: 'vendas', name: 'Relatório de Vendas' },
  { id: 'estoque', name: 'Relatório de Estoque' },
  { id: 'financeiro', name: 'Relatório Financeiro' },
  { id: 'clientes', name: 'Relatório de Clientes' }
];

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [reportType, setReportType] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !reportType) {
      setMessage('Por favor, selecione um arquivo e um tipo de relatório');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('reportType', reportType);

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

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold mb-8 text-center">Atualização de Relatórios</h1>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Relatório
            </label>
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Selecione um tipo</option>
              {reportTypes.map((type) => (
                <option key={type.id} value={type.id}>
                  {type.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Arquivo Excel
            </label>
            <input
              type="file"
              accept=".xlsx,.xls"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-2 px-4 rounded-md text-white font-medium 
              ${loading 
                ? 'bg-gray-400' 
                : 'bg-blue-600 hover:bg-blue-700'}`}
          >
            {loading ? 'Enviando...' : 'Enviar Arquivo'}
          </button>
        </form>

        {message && (
          <div className={`mt-4 p-4 rounded-md ${
            message.includes('Erro') 
              ? 'bg-red-100 text-red-700' 
              : 'bg-green-100 text-green-700'
          }`}>
            {message}
          </div>
        )}
      </div>
    </main>
  );
}

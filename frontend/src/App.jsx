import React, { useState, useEffect } from 'react';
import './App.css';

// Use Vite env var VITE_API_BASE (set in .env or in hosting). Fallback to localhost:8000 for local dev.
const API_BASE_URL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

function App() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [category, setCategory] = useState([]);
  const [appliedCategories, setAppliedCategories] = useState([]);

  useEffect(() => {
    // Only fetch when the user has applied category filters
    if (appliedCategories && appliedCategories.length > 0) {
      fetchProducts(appliedCategories);
    } else {
      // clear products until a filter is applied
      setProducts([]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(appliedCategories)]);

  const fetchProducts = async (categories = []) => {
    setLoading(true);
    setError(null);
    
    try {
      // New backend exposes paginated endpoint at /v1/products
      const params = new URLSearchParams({ page: '1', page_size: '100' });
      if (Array.isArray(categories) && categories.length > 0) {
        categories.forEach((c) => params.append('category', c));
      }
      const response = await fetch(`${API_BASE_URL}/v1/products?${params.toString()}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Backend returns a PaginatedResponse { items, total, page, page_size }
      if (data && Array.isArray(data.items)) {
        setProducts(data.items);
      } else {
        setError('Unexpected response format from server');
      }
    } catch (err) {
      console.error('Fetch error:', err);
      setError('Network error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleProductSelection = (productId) => {
    console.log('Toggling product:', productId); // Debug
    console.log('Current selected:', selectedProducts); // Debug
    
    if (selectedProducts.includes(productId)) {
      setSelectedProducts(selectedProducts.filter(id => id !== productId));
    } else if (selectedProducts.length < 5) {
      setSelectedProducts([...selectedProducts, productId]);
    }
  };

  const compareProducts = async () => {
    if (selectedProducts.length < 2) {
      alert('Please select at least 2 products to compare');
      return;
    }

    // The backend does not provide a compare endpoint; perform comparison on the client
    setLoading(true);
    try {
      const productsToCompare = products.filter(p => selectedProducts.includes(p.id));

      // Compute summary
      const prices = productsToCompare.map(p => Number(p.price) || 0);
      const ratings = productsToCompare.map(p => Number(p.rating) || 0);
      const categories = Array.from(new Set(productsToCompare.map(p => p.category).filter(Boolean)));

      const summary = {
        price_range: {
          min: Math.min(...prices),
          max: Math.max(...prices)
        },
        average_rating: ratings.length ? (ratings.reduce((a,b) => a + b, 0) / ratings.length) : 0,
        categories
      };

      setComparisonResult({ products: productsToCompare, comparison_summary: summary });
    } catch (err) {
      console.error('Comparison error:', err);
      setError('Comparison error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const clearSelection = () => {
    setSelectedProducts([]);
    setComparisonResult(null);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  // Debug: sempre mostrar quantos produtos estão selecionados
  console.log('Selected products count:', selectedProducts.length);

  return (
    <div className="App">
      <header className="app-header">
        <div className="container">
          <h1>🛍️ Product Comparison Hub</h1>
          <p>Compare the latest tech products with advanced filtering</p>
        </div>
      </header>

      <div className="container">
        {/* DEBUG: Sempre mostrar o contador */}
        <div style={{
          background: '#f0f0f0', 
          padding: '10px', 
          margin: '10px 0', 
          borderRadius: '5px',
          textAlign: 'center'
        }}>
          <strong>DEBUG: {selectedProducts.length} produtos selecionados</strong>
          {selectedProducts.length > 0 && (
            <div>IDs: {selectedProducts.join(', ')}</div>
          )}
        </div>

        {/* CATEGORY FILTER - user must Apply to load products */}
        <div style={{margin: '0 0 1.5rem 0', textAlign: 'center'}}>
          <label htmlFor="category" style={{display: 'block', marginBottom: '8px'}}>Escolha categoria(s) e clique em Apply:</label>
          <div style={{display: 'inline-flex', gap: '8px', alignItems: 'center'}}>
            <select id="category" multiple value={category} onChange={(e) => {
              const selected = Array.from(e.target.selectedOptions).map(o => o.value);
              setCategory(selected);
            }} style={{minWidth: '260px', padding: '8px'}}>
              <option value="Laptops">Laptops</option>
              <option value="Smartphones">Smartphones</option>
              <option value="Headphones">Headphones</option>
              <option value="TVs">TVs</option>
            </select>
            <button onClick={() => setAppliedCategories(category)} disabled={category.length === 0} style={{padding: '8px 12px'}}>
              Apply filter
            </button>
            <button onClick={() => { setCategory([]); setAppliedCategories([]); setProducts([]); }} style={{padding: '8px 12px'}}>
              Clear
            </button>
          </div>
        </div>

        {/* COMPARISON SECTION - SEMPRE VISÍVEL QUANDO HÁ PRODUTOS SELECIONADOS */}
        {selectedProducts.length > 0 && (
          <div style={{
            background: 'rgba(40, 167, 69, 0.1)',
            border: '2px solid #28a745',
            borderRadius: '16px',
            padding: '2rem',
            marginBottom: '2rem',
            textAlign: 'center'
          }}>
            <h3 style={{color: '#28a745', marginBottom: '1rem'}}>
              🎯 {selectedProducts.length} produto(s) selecionado(s) para comparação
            </h3>
            
            <div style={{display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap'}}>
              <button 
                onClick={compareProducts}
                disabled={selectedProducts.length < 2 || loading}
                style={{
                  background: selectedProducts.length >= 2 ? '#28a745' : '#ccc',
                  color: 'white',
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  cursor: selectedProducts.length >= 2 ? 'pointer' : 'not-allowed'
                }}
              >
                {loading ? '🔄 Comparando...' : '📊 Comparar Produtos Selecionados'}
              </button>
              
              <button 
                onClick={clearSelection}
                style={{
                  background: '#dc3545',
                  color: 'white',
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  cursor: 'pointer'
                }}
              >
                🗑️ Limpar Seleção
              </button>
            </div>
            
            {selectedProducts.length < 2 && (
              <p style={{color: '#666', marginTop: '1rem', fontStyle: 'italic'}}>
                Selecione pelo menos 2 produtos para comparar
              </p>
            )}
          </div>
        )}

        {/* COMPARISON RESULTS */}
        {comparisonResult && (
          <div style={{
            background: 'white',
            borderRadius: '16px',
            padding: '2rem',
            marginBottom: '2rem',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
          }}>
            <h2 style={{textAlign: 'center', marginBottom: '2rem'}}>📊 Resultados da Comparação</h2>
            
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '1rem',
              marginBottom: '2rem'
            }}>
              <div style={{background: '#667eea', color: 'white', padding: '1rem', borderRadius: '8px', textAlign: 'center'}}>
                <h4>💰 Faixa de Preço</h4>
                <p>{formatPrice(comparisonResult.comparison_summary.price_range.min)} - {formatPrice(comparisonResult.comparison_summary.price_range.max)}</p>
              </div>
              <div style={{background: '#667eea', color: 'white', padding: '1rem', borderRadius: '8px', textAlign: 'center'}}>
                <h4>⭐ Rating Médio</h4>
                <p>{comparisonResult.comparison_summary.average_rating.toFixed(1)} ⭐</p>
              </div>
              <div style={{background: '#667eea', color: 'white', padding: '1rem', borderRadius: '8px', textAlign: 'center'}}>
                <h4>📂 Categorias</h4>
                <p>{comparisonResult.comparison_summary.categories.join(', ')}</p>
              </div>
            </div>

            <div style={{overflowX: 'auto'}}>
              <table style={{width: '100%', borderCollapse: 'collapse', background: 'white'}}>
                <thead>
                  <tr style={{background: '#f8f9fa'}}>
                    <th style={{padding: '1rem', textAlign: 'left', borderBottom: '1px solid #ddd'}}>Produto</th>
                    <th style={{padding: '1rem', textAlign: 'left', borderBottom: '1px solid #ddd'}}>Preço</th>
                    <th style={{padding: '1rem', textAlign: 'left', borderBottom: '1px solid #ddd'}}>Rating</th>
                    <th style={{padding: '1rem', textAlign: 'left', borderBottom: '1px solid #ddd'}}>Categoria</th>
                    <th style={{padding: '1rem', textAlign: 'left', borderBottom: '1px solid #ddd'}}>Marca</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonResult.products.map(product => (
                    <tr key={product.id}>
                      <td style={{padding: '1rem', borderBottom: '1px solid #ddd'}}>
                        <div style={{display: 'flex', alignItems: 'center', gap: '1rem'}}>
                          <img src={product.image_url} alt={product.name} style={{width: '50px', height: '50px', objectFit: 'cover', borderRadius: '4px'}} />
                          <div>
                            <strong>{product.name}</strong>
                            <p style={{color: '#666', fontSize: '0.9rem', margin: '4px 0 0 0'}}>{product.description.substring(0, 80)}...</p>
                          </div>
                        </div>
                      </td>
                      <td style={{padding: '1rem', borderBottom: '1px solid #ddd', color: '#28a745', fontWeight: 'bold'}}>{formatPrice(product.price)}</td>
                      <td style={{padding: '1rem', borderBottom: '1px solid #ddd'}}>{product.rating} ⭐</td>
                      <td style={{padding: '1rem', borderBottom: '1px solid #ddd'}}>{product.category}</td>
                      <td style={{padding: '1rem', borderBottom: '1px solid #ddd'}}>{product.brand}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div style={{textAlign: 'center', marginTop: '2rem'}}>
              <button 
                onClick={clearSelection}
                style={{
                  background: '#6c757d',
                  color: 'white',
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  cursor: 'pointer'
                }}
              >
                🔄 Nova Comparação
              </button>
            </div>
          </div>
        )}

        {/* LOADING */}
        {loading && (
          <div style={{textAlign: 'center', padding: '2rem'}}>
            <div style={{
              width: '40px', 
              height: '40px', 
              border: '4px solid #f3f3f3', 
              borderTop: '4px solid #667eea', 
              borderRadius: '50%', 
              animation: 'spin 1s linear infinite',
              margin: '0 auto 1rem'
            }}></div>
            <p>Carregando produtos...</p>
          </div>
        )}

        {/* ERROR */}
        {error && (
          <div style={{
            textAlign: 'center', 
            padding: '2rem', 
            background: 'rgba(220, 53, 69, 0.1)', 
            border: '2px solid rgba(220, 53, 69, 0.3)', 
            borderRadius: '12px',
            margin: '2rem 0'
          }}>
            <p style={{color: '#dc3545', marginBottom: '1rem', fontWeight: '600'}}>❌ {error}</p>
            <button 
              onClick={fetchProducts} 
              style={{
                background: '#dc3545',
                color: 'white',
                border: 'none',
                padding: '8px 16px',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Tentar Novamente
            </button>
          </div>
        )}

        {/* PRODUCTS */}
        {!loading && !error && (
          <div style={{marginBottom: '2rem'}}>
            <div style={{
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center', 
              marginBottom: '2rem',
              background: 'rgba(255, 255, 255, 0.95)',
              padding: '1.5rem',
              borderRadius: '16px'
            }}>
              <h2 style={{margin: 0}}>🛒 Produtos ({products.length})</h2>
              {selectedProducts.length > 0 && (
                <span style={{
                  background: '#28a745',
                  color: 'white',
                  padding: '8px 16px',
                  borderRadius: '20px',
                  fontSize: '0.9rem'
                }}>
                  {selectedProducts.length} selecionado(s)
                </span>
              )}
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
              gap: '2rem'
            }}>
              {products.map(product => (
                <div 
                  key={product.id} 
                  style={{
                    background: selectedProducts.includes(product.id) ? 'rgba(40, 167, 69, 0.05)' : 'white',
                    borderRadius: '12px',
                    overflow: 'hidden',
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                    border: selectedProducts.includes(product.id) ? '2px solid #28a745' : '2px solid transparent',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <div style={{height: '200px', overflow: 'hidden', position: 'relative'}}>
                    <img 
                      src={product.image_url} 
                      alt={product.name} 
                      style={{width: '100%', height: '100%', objectFit: 'cover'}}
                    />
                    {selectedProducts.includes(product.id) && (
                      <div style={{
                        position: 'absolute',
                        top: '10px',
                        left: '10px',
                        background: '#28a745',
                        color: 'white',
                        padding: '4px 8px',
                        borderRadius: '12px',
                        fontSize: '0.8rem'
                      }}>
                        ✓ Selecionado
                      </div>
                    )}
                  </div>

                  <div style={{padding: '1.5rem'}}>
                    <h3 style={{margin: '0 0 0.5rem 0'}}>{product.name}</h3>
                    <p style={{
                      background: '#667eea',
                      color: 'white',
                      padding: '4px 8px',
                      borderRadius: '4px',
                      fontSize: '0.8rem',
                      display: 'inline-block',
                      margin: '0 0 1rem 0'
                    }}>
                      {product.brand}
                    </p>
                    <p style={{color: '#666', marginBottom: '1rem', lineHeight: '1.4'}}>{product.description}</p>
                    <p style={{color: '#888', fontSize: '0.9rem', marginBottom: '0.5rem'}}>{product.category}</p>
                    <p style={{color: '#888', fontSize: '0.9rem', marginBottom: '1rem'}}>Rating: {product.rating}⭐</p>
                    
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}>
                      <div style={{
                        fontSize: '1.5rem',
                        fontWeight: '700',
                        color: '#28a745'
                      }}>
                        {formatPrice(product.price)}
                      </div>
                      <button
                        onClick={() => toggleProductSelection(product.id)}
                        style={{
                          background: selectedProducts.includes(product.id) ? '#28a745' : 'transparent',
                          color: selectedProducts.includes(product.id) ? 'white' : '#667eea',
                          border: `2px solid ${selectedProducts.includes(product.id) ? '#28a745' : '#667eea'}`,
                          padding: '8px 16px',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          fontSize: '0.9rem'
                        }}
                      >
                        {selectedProducts.includes(product.id) ? '✓ Selecionado' : '+ Selecionar'}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <footer style={{
        background: 'rgba(255, 255, 255, 0.95)',
        padding: '2rem 0',
        marginTop: '2rem',
        textAlign: 'center'
      }}>
        <div className="container">
          <p>🚀 Product Comparison API - Built with React & Vite</p>
        </div>
      </footer>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default App;
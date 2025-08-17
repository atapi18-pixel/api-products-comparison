import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export default function App() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [category, setCategory] = useState([]);
  const [appliedCategories, setAppliedCategories] = useState([]);
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [comparisonResult, setComparisonResult] = useState(null);

  useEffect(() => {
    // fetch only when the user has applied a category filter
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
      const params = new URLSearchParams({ page: '1', page_size: '100' });
      // append multiple category params when present
      if (Array.isArray(categories) && categories.length > 0) {
        categories.forEach((c) => params.append('category', c));
      }
      const res = await fetch(`${API_BASE_URL}/v1/products?${params.toString()}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (data && Array.isArray(data.items)) setProducts(data.items);
      else setError('Unexpected response format from server');
    } catch (err) {
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  };

        const toggleProductSelection = (id) => {
          setSelectedProducts((cur) => {
            if (cur.includes(id)) {
              return cur.filter((x) => x !== id);
            } else if (cur.length < 5) {
              return [...cur, id];
            } else {
              return cur;
            }
          });
        };

        const compareProducts = () => {
          if (selectedProducts.length < 2) {
            alert('Please select at least 2 products to compare');
            return;
          }
          const toCompare = products.filter((p) => selectedProducts.includes(p.id));
          const prices = toCompare.map((p) => Number(p.price) || 0);
          const ratings = toCompare.map((p) => Number(p.rating) || 0);
          const categories = Array.from(new Set(toCompare.map((p) => p.category).filter(Boolean)));

          const summary = {
            price_range: { min: prices.length ? Math.min(...prices) : 0, max: prices.length ? Math.max(...prices) : 0 },
            average_rating: ratings.length ? ratings.reduce((a, b) => a + b, 0) / ratings.length : 0,
            categories,
          };

          setComparisonResult({ products: toCompare, comparison_summary: summary });
        };

        const clearSelection = () => {
          setSelectedProducts([]);
          setComparisonResult(null);
        };

        const formatPrice = (price) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(price || 0);

        return (
          <div className="App">
            <header className="app-header">
              <div className="container">
                <h1>🛍️ Product Comparison Hub</h1>
                <p>Compare the latest tech products</p>
              </div>
            </header>

            <main className="container">
              <div className="debug">
                <strong>DEBUG: {selectedProducts.length} selected</strong>
              </div>

              <div className="filters">
                <label htmlFor="category">Choose category(ies) and click Apply to list products:</label>
                <div className="filter-controls">
                  <select id="category" multiple value={category} onChange={(e) => {
                    const selected = Array.from(e.target.selectedOptions).map(o => o.value);
                    setCategory(selected);
                  }}>
                    <option value="Laptops">Laptops</option>
                    <option value="Smartphones">Smartphones</option>
                    <option value="Headphones">Headphones</option>
                    <option value="TVs">TVs</option>
                  </select>
                  <button className="apply" onClick={() => setAppliedCategories(category)} disabled={category.length === 0}>
                    Apply filter
                  </button>
                  <button className="clear" onClick={() => { setCategory([]); setAppliedCategories([]); setProducts([]); }}>
                    Clear
                  </button>
                </div>
              </div>

      {selectedProducts.length > 0 && (
                <section className="compare-panel">
                  <h3>{selectedProducts.length} produto(s) selecionado(s)</h3>
                  <div className="actions">
        <button onClick={compareProducts} disabled={selectedProducts.length < 2 || loading}>
                      📊 Comparar
                    </button>
                    <button onClick={clearSelection}>🗑️ Limpar</button>
                  </div>
                  {selectedProducts.length < 2 && <p>Selecione pelo menos 2 produtos para comparar</p>}
                </section>
              )}

              {comparisonResult && (
                <section className="comparison-results">
                  <h2>📊 Resultados</h2>
                  <div className="summary">
                    <div>
                      <strong>Faixa de preço</strong>
                      <div>{formatPrice(comparisonResult.comparison_summary.price_range.min)} - {formatPrice(comparisonResult.comparison_summary.price_range.max)}</div>
                    </div>
                    <div>
                      <strong>Rating médio</strong>
                      <div>{comparisonResult.comparison_summary.average_rating.toFixed(1)} ⭐</div>
                    </div>
                    <div>
                      <strong>Categorias</strong>
                      <div>{comparisonResult.comparison_summary.categories.join(', ')}</div>
                    </div>
                  </div>

                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>Produto</th>
                          <th>Preço</th>
                          <th>Rating</th>
                          <th>Categoria</th>
                          <th>Marca</th>
                        </tr>
                      </thead>
                      <tbody>
                        {comparisonResult.products.map((p) => (
                          <tr key={p.id}>
                            <td>
                              <div className="product-cell">
                                {p.image_url && <img src={p.image_url} alt={p.name} />}
                                <div>
                                  <strong>{p.name}</strong>
                                  <div className="muted">{p.description?.substring(0, 80)}...</div>
                                </div>
                              </div>
                            </td>
                            <td>{formatPrice(p.price)}</td>
                            <td>{p.rating}</td>
                            <td>{p.category}</td>
                            <td>{p.brand}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </section>
              )}

              {loading && <div className="loading">Carregando...</div>}

              {error && (
                <div className="error">
                  <p>❌ {error}</p>
                  <button onClick={fetchProducts}>Tentar novamente</button>
                </div>
              )}

              {!loading && !error && (
                <section className="products-list">
                  <h2>🛒 Produtos ({products.length})</h2>
                  <div className="grid">
                    {products.map((product) => (
                      <article key={product.id} className={`card ${selectedProducts.includes(product.id) ? 'selected' : ''}`}>
                        <div className="media">
                          {product.image_url && <img src={product.image_url} alt={product.name} />}
                        </div>
                        <div className="body">
                          <h3>{product.name}</h3>
                          <div className="brand">{product.brand}</div>
                          <p className="desc">{product.description}</p>
                          <div className="row">
                            <div className="price">{formatPrice(product.price)}</div>
                            {(() => {
                              let buttonLabel;
                              if (selectedProducts.includes(product.id)) {
                                buttonLabel = 'Remover';
                              } else if (appliedCategories.length === 0) {
                                buttonLabel = 'Select a category first';
                              } else {
                                buttonLabel = 'Selecionar';
                              }
                              return (
                                <button onClick={() => toggleProductSelection(product.id)} disabled={appliedCategories.length === 0}>
                                  {buttonLabel}
                                </button>
                              );
                            })()}
                          </div>
                        </div>
                      </article>
                    ))}
                  </div>
                </section>
              )}
            </main>
          </div>
        );
      }
import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import Router from './router';
import { Toaster } from 'react-hot-toast';

const App = () => {
  return (
    <BrowserRouter>
      <Router />
      <Toaster />
    </BrowserRouter>
  );
};

export default App;

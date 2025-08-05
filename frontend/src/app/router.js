import React from 'react';
import { Routes, Route } from 'react-router-dom';
import MainPage from '@/pages/Main/MainPage';


const Router = () => {
  return (
    <Routes>
      <Route path="/" element={<MainPage />} />
    </Routes>
  );
};

export default Router;

-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Tempo de geração: 22-Maio-2025 às 20:03
-- Versão do servidor: 9.2.0
-- versão do PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Banco de dados: `leafy`
--

-- --------------------------------------------------------

--
-- Estrutura da tabela `plants`
--

CREATE TABLE `plants` (
  `id` bigint UNSIGNED NOT NULL,
  `name` varchar(100) NOT NULL,
  `waterMin` smallint DEFAULT NULL,
  `waterMax` smallint DEFAULT NULL,
  `tempMin` decimal(4,1) DEFAULT NULL,
  `tempMax` decimal(4,1) DEFAULT NULL,
  `umidMin` smallint DEFAULT NULL,
  `umidMax` smallint DEFAULT NULL,
  `lumMin` int DEFAULT NULL,
  `lumMax` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Extraindo dados da tabela `plants`
--

INSERT INTO `plants` (`id`, `name`, `waterMin`, `waterMax`, `tempMin`, `tempMax`, `umidMin`, `umidMax`, `lumMin`, `lumMax`) VALUES
(1, 'Alface', 40, 78, 16.0, 24.0, 50, 70, 5000, 15000),
(2, 'Tomate', 60, 80, 18.0, 30.0, 60, 70, 8000, 32000),
(3, 'Manjericão', 50, 75, 20.0, 30.0, 50, 80, 10000, 20000),
(4, 'Espinafre', 50, 70, 10.0, 24.0, 60, 80, 2000, 5000),
(5, 'Pimento', 60, 80, 18.0, 30.0, 60, 80, 8000, 20000),
(6, 'Pepino', 70, 90, 18.0, 27.0, 60, 80, 10000, 25000),
(7, 'Morango', 60, 80, 15.0, 25.0, 60, 80, 10000, 20000),
(8, 'Couve', 50, 75, 15.0, 24.0, 60, 80, 5000, 10000),
(9, 'Cenoura', 60, 80, 16.0, 24.0, 50, 70, 10000, 20000),
(10, 'Cebolinha', 50, 75, 15.0, 25.0, 60, 80, 5000, 15000);

-- --------------------------------------------------------

--
-- Estrutura da tabela `users`
--

CREATE TABLE `users` (
  `id` int NOT NULL,
  `telegramId` bigint NOT NULL,
  `name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Extraindo dados da tabela `users`
--

INSERT INTO `users` (`id`, `telegramId`, `name`) VALUES
(1, 5830766951, 'Pedro_Leandr'),
(2, 7521222902, 'Bernardo');

-- --------------------------------------------------------

--
-- Estrutura da tabela `vases`
--

CREATE TABLE `vases` (
  `id` varchar(255) NOT NULL,
  `plantId` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Extraindo dados da tabela `vases`
--

INSERT INTO `vases` (`id`, `plantId`) VALUES
('LEAFY-119540', 5),
('LEAFY-674121', NULL),
('LEAFY-991714', NULL);

-- --------------------------------------------------------

--
-- Estrutura da tabela `vases_users`
--

CREATE TABLE `vases_users` (
  `vaseId` varchar(255) NOT NULL,
  `userId` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Extraindo dados da tabela `vases_users`
--

INSERT INTO `vases_users` (`vaseId`, `userId`) VALUES
('LEAFY-119540', 1);

--
-- Índices para tabelas despejadas
--

--
-- Índices para tabela `plants`
--
ALTER TABLE `plants`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `id` (`id`);

--
-- Índices para tabela `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- Índices para tabela `vases`
--
ALTER TABLE `vases`
  ADD PRIMARY KEY (`id`);

--
-- Índices para tabela `vases_users`
--
ALTER TABLE `vases_users`
  ADD PRIMARY KEY (`vaseId`,`userId`),
  ADD KEY `userId` (`userId`);

--
-- AUTO_INCREMENT de tabelas despejadas
--

--
-- AUTO_INCREMENT de tabela `plants`
--
ALTER TABLE `plants`
  MODIFY `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de tabela `users`
--
ALTER TABLE `users`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Restrições para despejos de tabelas
--

--
-- Limitadores para a tabela `vases_users`
--
ALTER TABLE `vases_users`
  ADD CONSTRAINT `vases_users_ibfk_1` FOREIGN KEY (`vaseId`) REFERENCES `vases` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `vases_users_ibfk_2` FOREIGN KEY (`userId`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

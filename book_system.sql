-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 12, 2025 at 09:07 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `book_system`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `username`, `password`) VALUES
(1, 'Ritu', '$2b$12$LZof5nTiUjuMmS4B8XeDbeidbteU6bDpdo6.pCkJ5W4VHJE7YZ.zC'),
(2, 'Khushbu', '$2b$12$KmcfP6NTYy4BLSmPTY82JeihwA4QiGb0S6qTfQpGv2TPwqevZHT/q');

-- --------------------------------------------------------

--
-- Table structure for table `books`
--

CREATE TABLE `books` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `author` varchar(255) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `year` varchar(10) DEFAULT NULL,
  `pdf_file` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `books`
--

INSERT INTO `books` (`id`, `title`, `author`, `category`, `year`, `pdf_file`) VALUES
(2, 'Harry potter', '', NULL, NULL, NULL),
(4, 'Data Compression', 'Khalid Sayood', NULL, NULL, '6722_Book.pdf');

-- --------------------------------------------------------

--
-- Table structure for table `favorites`
--

CREATE TABLE `favorites` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `book_id` varchar(200) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `author` varchar(255) DEFAULT NULL,
  `image` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `favorites`
--

INSERT INTO `favorites` (`id`, `user_id`, `book_id`, `title`, `author`, `image`) VALUES
(1, 6, 'fFCjDQAAQBAJ', 'Atomic Habits', 'James Clear', 'http://books.google.com/books/publisher/content?id=fFCjDQAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&imgtk=AFLRE71oX6ajmK85RycXdonkOkNqiaH5VKmAZFz5mr6Y5QxjQUNEhracLUJV3lboGW-qb1thVysBn9fFIAQHltOj2yt5F5uCmoy_1hSiLkxbgK0E4CVvlr1MX5heSlHpmDYb8p3rMFKY&source=gbs_api'),
(2, 6, 'r6UyEAAAQBAJ', 'Harry Potter Box Set: the Complete Collection (Children\'s Paperback)', 'J. K. Rowling', 'http://books.google.com/books/content?id=r6UyEAAAQBAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api'),
(3, 6, 'fFCjDQAAQBAJ', 'Atomic Habits', 'James Clear', 'http://books.google.com/books/publisher/content?id=fFCjDQAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&imgtk=AFLRE72Oltt2QDBJEzTeqvgiXnDUDd-Me6nq0NYXvHrGipSBT_1CuGEBLmBABn7UPcotCwbqt4e15TYaBi7-P9gHpKu_ylLmbht9F2USbZ_VcR7_rfsM0_gYKdFKLFQircA0ctP3bD_B&source=gbs_api'),
(4, 6, '2WsnLilhMYkC', 'Bhagavad Gita', 'Unknown', 'http://books.google.com/books/content?id=2WsnLilhMYkC&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api'),
(5, 7, '2WsnLilhMYkC', 'Bhagavad Gita', 'Unknown', 'http://books.google.com/books/content?id=2WsnLilhMYkC&printsec=frontcover&img=1&zoom=1&edge=curl&imgtk=AFLRE72yBjj4HrKNX6srNZS6KSqq1Wadh05XwETtPwGipN5n8v9Zq-i55I-nCeKPrjWPS_Ryv3kM6dngnWOJ4xz3j5DsL4AHxz2OmXcpN5o2jaAmFPXsJTVdOEOI9hRFAaj1Gpvsw2xH&source=gbs_api');

-- --------------------------------------------------------

--
-- Table structure for table `reviews`
--

CREATE TABLE `reviews` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `book_id` varchar(255) DEFAULT NULL,
  `review` text DEFAULT NULL,
  `rating` int(11) DEFAULT NULL,
  `approved` tinyint(1) DEFAULT 0,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `search_history`
--

CREATE TABLE `search_history` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `query` varchar(255) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `search_history`
--

INSERT INTO `search_history` (`id`, `user_id`, `query`, `timestamp`) VALUES
(1, 6, 'harry potter', '2025-11-28 17:31:59'),
(2, 6, 'atomic habits', '2025-11-28 17:32:46'),
(3, 6, 'harry potter', '2025-11-28 17:33:43'),
(4, 6, 'harry potter', '2025-11-28 17:39:39'),
(5, 6, 'atomic habits', '2025-11-28 17:42:05'),
(6, 6, 'atomic habits', '2025-11-28 17:49:01'),
(7, 6, 'atomic habits', '2025-11-28 17:50:32'),
(8, 6, 'bhagvad geeta', '2025-11-28 17:54:16'),
(9, 6, 'atomic habits', '2025-11-28 17:54:54'),
(10, 6, 'harry potter', '2025-11-28 17:55:30'),
(11, 6, 'mahabharat', '2025-11-28 17:55:51'),
(12, 6, 'mahabharat', '2025-11-28 18:00:40'),
(13, 7, 'bhagvad geeta', '2025-12-11 18:17:26'),
(14, 7, 'bhagvad geeta', '2025-12-11 18:18:23');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password`, `created_at`) VALUES
(1, 'khushi', 'khushbujadav6604@gmail.com', '$2b$12$Hac99aTd4EDwk6IDTeeVW..EqhiqUWF/rFVrWmLqAtG9TJesdZdv.', '2025-12-12 06:18:41'),
(2, 'Krutika', 'krutikajadav9702@gmail.com', '$2b$12$9UZ3feRTfcsAp7cweFHipO7rVDFnLGO3wSRgTWrEKxbD4Qo1jVLie', '2025-12-12 06:18:41'),
(6, 'Ritu', 'valandritu43@gmail.com', '$2b$12$fBch6n.7GrLwm9Sn.oqb3uWLeeWOnK9XpkvFqFRfYFNy4zaiYXMKi', '2025-12-12 06:18:41'),
(7, '2user', 'user2@gmail.com', '$2b$12$1TaGprRYjxzXMFySHwSuJukm3eXhtpw62uESPjPrd0id///0qEQty', '2025-12-12 06:18:41');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `books`
--
ALTER TABLE `books`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `favorites`
--
ALTER TABLE `favorites`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `reviews`
--
ALTER TABLE `reviews`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `search_history`
--
ALTER TABLE `search_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `books`
--
ALTER TABLE `books`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `favorites`
--
ALTER TABLE `favorites`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `reviews`
--
ALTER TABLE `reviews`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `search_history`
--
ALTER TABLE `search_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `favorites`
--
ALTER TABLE `favorites`
  ADD CONSTRAINT `favorites_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `reviews`
--
ALTER TABLE `reviews`
  ADD CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `search_history`
--
ALTER TABLE `search_history`
  ADD CONSTRAINT `search_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

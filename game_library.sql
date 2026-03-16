
CREATE DATABASE IF NOT EXISTS game_library;

-- Use the newly created database
USE game_library;

-- Temporarily disable foreign key checks to allow dropping tables in any order
SET FOREIGN_KEY_CHECKS = 0;

-- Drop tables if they exist to allow for a clean setup
DROP TABLE IF EXISTS Reviews;
DROP TABLE IF EXISTS Wishlist; -- Also drop Wishlist here
DROP TABLE IF EXISTS Games;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Genres;
DROP TABLE IF EXISTS Platforms;

-- Re-enable foreign key checks right after dropping
SET FOREIGN_KEY_CHECKS = 1;

-- Create Genres table
CREATE TABLE Genres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

-- Create Platforms table
CREATE TABLE Platforms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

-- Create Users table
CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

-- Create Games table, now with an image and description column
CREATE TABLE Games (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    genre_id INT,
    platform_id INT,
    release_year INT,
    publisher VARCHAR(255),
    image VARCHAR(255),
    description TEXT,
    FOREIGN KEY (genre_id) REFERENCES Genres(id),
    FOREIGN KEY (platform_id) REFERENCES Platforms(id)
);

-- Create Wishlist table (CORRECT POSITION)
CREATE TABLE Wishlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    game_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (game_id) REFERENCES Games(id) ON DELETE CASCADE,
    UNIQUE(user_id, game_id) -- Ensures a user cannot wishlist the same game twice
);

-- Create Reviews table
CREATE TABLE Reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    game_id INT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    date DATE,
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (game_id) REFERENCES Games(id)
);

-- Add a 'role' column to the Users table with a default value of 'user'
ALTER TABLE Users
ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'user';

-- Add a 'developer_id' column to the Games table to link it to a user
ALTER TABLE Games
ADD COLUMN developer_id INT,
ADD FOREIGN KEY (developer_id) REFERENCES Users(id) ON DELETE SET NULL;


-- Populate the Genres table with initial and new genres
INSERT INTO Genres (name) VALUES
('RPG'),
('Action RPG'),
('FPS'),
('Action-Adventure'),
('Sandbox'),
('MOBA'),
('Strategy'),
('Simulation'),
('Horror'),
('Sports'),
('Puzzle'),
('Racing'),
('Platformer'),
('Survival');

-- Populate the Platforms table with initial and new platforms
INSERT INTO Platforms (name) VALUES
('PC'),
('PS5'),
('Xbox'),
('PS4'),
('Multi-platform'),
('Nintendo Switch'),
('PS3'),
('Xbox 360');

-- Populate the Users table with mock data
-- Note: These are plaintext passwords and will need to be updated via registration for login to work
INSERT INTO Users (name, email, password_hash, role) VALUES
('Alice', 'alice@example.com', 'scrypt:32768:8:1$N2bmJwYou0nPsNA7$279883cc00117de0392c4836b749813f79530554bbf26bc66afb4d1485da104db8cacb8d607cf8a85cce5f0dcc393127faff6d969d79fe684a2becfa7b8dc283', 'user'),
('Bob', 'bob@example.com', 'scrypt:32768:8:1$YWCOHG1Zw27JMMv4$1b7f6d1601a1e1a2ace554d68c60cda05d9961fa4594fc4231f7a626295a13acd88015e2985e39be0031bbee6bed189be6407e368acaf3469df8055fda336517', 'user'),
('Admin User', 'admin@example.com', 'scrypt:32768:8:1$WmNXKccWZoegWqld$fd3528ab2942893208b23f6d8e406cd98459b0521943110e58d25411958c8296a0bba67c1a35714c6f181daf8dafe769de8323fcdbf93d3534895347f513472a', 'admin');


-- Populate the Games table with initial and new games, including descriptions
INSERT INTO Games (title, genre_id, platform_id, release_year, publisher, image, description) VALUES
-- Initial Games
('Cyberpunk 2077', 1, 1, 2020, 'CD Projekt', 'https://conceptartworld.com/wp-content/uploads/2020/01/The-World-of-Cyberpunk-2077-Art-Book-Header-01.jpg', 'An open-world, action-adventure story set in Night City, a megalopolis obsessed with power, glamour and body modification.'),
('Elden Ring', 2, 2, 2022, 'Bandai Namco', 'https://i.ytimg.com/vi/E3Huy2cdih0/sddefault.jpg', 'A fantasy action RPG with an immense world, intricate lore, and challenging combat.'),
('Valorant', 3, 1, 2020, 'Riot Games', 'https://mediaproxy.tvtropes.org/width/1200/https://static.tvtropes.org/pmwiki/pub/images/valo2.png', 'A 5v5 tactical shooter where agents with unique abilities clash on competitive maps.'),
('The Witcher 3: Wild Hunt', 2, 4, 2015, 'CD Projekt', 'https://store-images.s-microsoft.com/image/apps.46303.65858607118306853.39ed2a08-df0d-4ae1-aee0-c66ffb783a34.1fbbd7b6-6399-4b79-99f0-f48c6ada8a2b?q=90&w=480&h=270', 'An open-world RPG where you are Geralt of Rivia, a monster hunter, journeying to find a child of prophecy.'),
('God of War', 4, 4, 2018, 'Sony Interactive', 'https://cdn1.epicgames.com/offer/3ddd6a590da64e3686042d108968a6b2/EGS_GodofWar_SantaMonicaStudio_S2_1200x1600-fbdf3cbc2980749091d52751ffabb7b7_1200x1600-fbdf3cbc2980749091d52751ffabb7b7', 'Kratos returns in a new chapter, battling Norse mythology in a deeply emotional and violent journey.'),
('Minecraft', 5, 5, 2011, 'Mojang', 'https://upload.wikimedia.org/wikipedia/en/thumb/b/b6/Minecraft_2024_cover_art.png/250px-Minecraft_2024_cover_art.png', 'A sandbox game about placing blocks and going on adventures. Build anything you can imagine!'),
('League of Legends', 6, 1, 2009, 'Riot Games', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRI06jnEEVxi16_MKPOKeKRnaHuPy7jxM8vTA&s', 'A fast-paced, competitive online game where two teams of powerful champions battle to destroy the enemy''s base.'),
('Red Dead Redemption 2', 4, 4, 2018, 'Rockstar Games', 'https://upload.wikimedia.org/wikipedia/en/4/44/Red_Dead_Redemption_II.jpg', 'An epic tale of life in America''s unforgiving heartland. The game''s vast and atmospheric world will also provide the foundation for a brand new online multiplayer experience.'),
-- New Games
('StarCraft II', 7, 1, 2010, 'Blizzard Entertainment', 'https://upload.wikimedia.org/wikipedia/en/2/20/StarCraft_II_-_Box_Art.jpg', 'A real-time strategy game featuring three distinct races battling for galactic dominance in a sci-fi universe.'),
('The Sims 4', 8, 1, 2014, 'Electronic Arts', 'https://images-cdn.ubuy.co.in/633afd8d3f61cc07074aee88-the-sims-4-pc-mac.jpg', 'A life simulation game where you create and control people, build their homes, and guide their lives.'),
('Resident Evil Village', 9, 2, 2021, 'Capcom', 'https://upload.wikimedia.org/wikipedia/en/2/2c/Resident_Evil_Village.png', 'A survival horror game with a first-person perspective, combining action-packed combat with tense exploration.'),
('FIFA 23', 10, 2, 2022, 'Electronic Arts', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSntoswKEfWpIu4JfPnpGpeCh_tSxbCuiT6ZA&s', 'The latest installment in the popular football video game series, featuring updated teams, players, and gameplay modes.'),
('Portal 2', 11, 1, 2011, 'Valve', 'https://upload.wikimedia.org/wikipedia/en/thumb/f/f9/Portal2cover.jpg/250px-Portal2cover.jpg', 'A first-person puzzle game where you use a portal gun to solve a series of increasingly difficult challenges.'),
('Forza Horizon 5', 12, 3, 2021, 'Xbox Game Studios', 'https://image.api.playstation.com/vulcan/ap/rnd/202501/2717/42b3ee6b1b2094212231b0b0a82824f687fc5c4dc9bde31c.png', 'A high-octane racing game set in a vibrant and diverse open world recreation of Mexico.'),
('Super Mario Odyssey', 13, 6, 2017, 'Nintendo', 'https://upload.wikimedia.org/wikipedia/en/thumb/8/8d/Super_Mario_Odyssey.jpg/250px-Super_Mario_Odyssey.jpg', 'A 3D platformer where Mario explores diverse worlds, collecting Power Moons to rescue Princess Peach from Bowser.'),
('Rust', 14, 1, 2018, 'Facepunch Studios', 'https://cdn.mos.cms.futurecdn.net/MjuLaBZuzHHAwMWiPQp6fG.jpg', 'A multiplayer-only survival game where players must gather resources and craft items to survive in a harsh wilderness.'),
('Civilization VI', 7, 1, 2016, '2K Games', 'https://cdn1.epicgames.com/cd14dcaa4f3443f19f7169a980559c62/offer/EGS_SidMeiersCivilizationVI_FiraxisGames_S1-2560x1440-2fcd1c150ac6d8cdc672ae042d2dd179.jpg', 'A turn-based strategy game where you lead a civilization from the Stone Age to the Information Age.'),
('Cities: Skylines', 8, 1, 2015, 'Paradox Interactive', 'https://cdn1.epicgames.com/6009be9994c2409099588cde6f3a5ed0/offer/EGS_CitiesSkylines_ColossalOrder_S3-2560x1440-14df106873c918591e49bd9604841e83.jpg', 'A city-building simulation game that gives you the power to create and manage your own metropolis.'),
('Dead by Daylight', 9, 5, 2016, 'Behaviour Interactive', 'https://cdn1.epicgames.com/spt-assets/2b2299be8ae84d679d4dc57c55af1510/dead-by-daylight-1hg3x.jpg', 'A multiplayer survival horror game where one player takes on the role of a killer and the other four play as survivors.'),
('NBA 2K23', 10, 2, 2022, '2K Sports', 'https://cdn.cdkeys.com/media/catalog/product/a/p/apps.64306.71295133238032534.1de820af-1d18-49b2-9916-0df00df0df84_1_.jpg', 'A basketball simulation game featuring realistic gameplay, updated rosters, and various game modes.'),
('Stardew Valley', 8, 5, 2016, 'ConcernedApe', 'https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/413150/capsule_616x353.jpg?t=1754692865', 'A charming farming simulation RPG where you inherit your grandfather''s old farm plot and embark on a new life.'),
('Hollow Knight', 13, 5, 2017, 'Team Cherry', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSgEYdEMxwc6EOw5LhEmnQy0x6_Y5cnxgSa_Q&s', 'A beautifully hand-drawn 2D platformer set in the vast, interconnected world of Hallownest, a ruined kingdom of insects.'),
('Slay the Spire', 7, 1, 2019, 'MegaCrit', 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/646570/header.jpg?t=1745019194', 'A card-based rogue-like where you build a unique deck, encounter bizarre creatures, and discover relics of immense power.'),
('Fall Guys', 13, 5, 2020, 'Mediatonic', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR12ZK3IhJip_HEW-DMZvf7oGkT1wwSASNmtg&s', 'A battle royale game where up to 60 players control clumsy, jellybean-like characters to compete in a series of obstacle courses.'),
('The Last of Us', 4, 7, 2013, 'Naughty Dog', 'https://m.media-amazon.com/images/M/MV5BMTE2MmQ3OTctZmExNi00ZTYxLTgzMGYtOTdlYjFjNzIxNWMxXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg', 'An action-adventure survival horror game where a smuggler is tasked with escorting a teenage girl across a post-apocalyptic United States.'),
('Grand Theft Auto V', 4, 5, 2013, 'Rockstar Games', 'https://upload.wikimedia.org/wikipedia/en/a/a5/Grand_Theft_Auto_V.png', 'An open-world action-adventure game set in the sprawling city of Los Santos, following the lives of three different criminals.'),
('DOOM Eternal', 3, 5, 2020, 'id Software', 'https://upload.wikimedia.org/wikipedia/en/9/9d/Cover_Art_of_Doom_Eternal.png', 'The sequel to the 2016 DOOM, a fast-paced, visceral first-person shooter where you rip and tear through hordes of demons.'),
('Sekiro: Shadows Die Twice', 2, 5, 2019, 'FromSoftware', 'https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/814380/capsule_616x353.jpg?t=1754933982', 'A challenging action-adventure game set in feudal Japan, focusing on intense sword combat and stealth gameplay.');


-- Populate the Reviews table with initial data
INSERT INTO Reviews (user_id, game_id, rating, review_text, date) VALUES
(1, 1, 4, 'A beautiful but buggy world. The story is engaging though!', '2021-03-15'),
(2, 2, 5, 'An absolute masterpiece. The open world is incredible.', '2022-05-20'),
(3, 1, 3, 'The gameplay is a bit clunky, but the visuals are amazing.', '2021-04-10'),
(1, 4, 5, 'One of the best games ever made. A must-play.', '2016-01-05'),
(3, 2, 5, 'The boss fights are challenging and so rewarding!', '2022-06-01');

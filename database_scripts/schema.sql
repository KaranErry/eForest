-- Name characters: 50

CREATE TABLE Dept_M (
	abbr VARCHAR(4) PRIMARY KEY,
	chair BIGINT
);

CREATE TABLE Prof_M (
	id BIGSERIAL PRIMARY KEY,
	first_name VARCHAR(50) NOT NULL,
	last_name VARCHAR(50) NOT NULL,
	dept_abbr VARCHAR(4) REFERENCES Dept_M NOT NULL
);
ALTER TABLE Dept_M ADD FOREIGN KEY (chair) REFERENCES Prof_M;

CREATE TABLE Course_M (
	dept_abbr VARCHAR(4) REFERENCES Dept_M,
	number INT2,
	PRIMARY KEY( dept_abbr, number )
);


CREATE TABLE Student_P (
	id BIGSERIAL PRIMARY KEY,
	first_name VARCHAR(50) NOT NULL,
	last_name VARCHAR(50) NOT NULL,
	expected_grad BIT(15)
);

CREATE TYPE PROG_TYPE AS ENUM ( 'major', 'minor', 'program' );
CREATE TABLE Program_M (
	id SMALLSERIAL PRIMARY KEY,
	name VARCHAR(50) NOT NULL,
	type PROG_TYPE NOT NULL
);

CREATE TABLE Program_Members_M (
	program SMALLINT REFERENCES Program_M,
	student BIGINT REFERENCES Student_P,
	PRIMARY KEY (program, student)
);

CREATE TABLE Program_Courses_M (
	program SMALLINT REFERENCES Program_M,
	course_name VARCHAR(4),
	course_number INT2,
	FOREIGN KEY (course_name, course_number) REFERENCES Course_M (dept_abbr, number),
	PRIMARY KEY (program, course_name, course_number)
);

CREATE TABLE Course_Listing_S (
	section SERIAL PRIMARY KEY,
	professor BIGINT REFERENCES Prof_M,
	course_name VARCHAR(4) NOT NULL,
	course_number INT2 NOT NULL,
	seat_cap INT2,
	FOREIGN KEY (course_name, course_number) REFERENCES Course_M (dept_abbr, number)
);

CREATE TABLE Course_Pref_S (
	student BIGINT REFERENCES Student_P,
	course_name VARCHAR(4),
	course_number INT2,
	FOREIGN KEY (course_name, course_number) REFERENCES Course_M (dept_abbr, number),
	PRIMARY KEY (student, course_name, course_number)
);

CREATE TABLE Time_Block_M (
	name SMALLSERIAL PRIMARY KEY,
	start_time VARCHAR(25) NOT NULL,
	end_time VARCHAR(25) NOT NULL
);

CREATE TYPE TIME_PREF AS ENUM ( 'cannot', 'dislike', 'ok', 'like' );
CREATE TABLE Prof_Timing_S (
	section INT REFERENCES Course_Listing_S,
	block SMALLINT REFERENCES Time_Block_M,
	preference TIME_PREF,
	PRIMARY KEY ( section, block ) 
);

CREATE TABLE Room_M (
	id SERIAL PRIMARY KEY,
	building VARCHAR(50) NOT NULL,
	room_num INT2 NOT NULL
);

CREATE TABLE Room_Feature_M (
	id SERIAL PRIMARY KEY,
	description_str VARCHAR(50) NOT NULL
);

CREATE TABLE Room_Features_M (
	room INT REFERENCES Room_M,
	feature INT REFERENCES Room_Feature_M,
	PRIMARY KEY( room, feature )
);

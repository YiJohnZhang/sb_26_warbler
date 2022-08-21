# import sys
import csv

# input
with open('follows.csv',newline='') as csvReadFile:
    csvObject = csv.DictReader(csvReadFile, delimiter=",");
    csvHeader = next(csvObject);
    
    csvTupleList = [];

    for dataRow in csvObject:
        csvTupleList.append((int(dataRow['user_being_followed_id']), int(dataRow['user_following_id'])));

    initialSortedList = sorted(csvTupleList, key = lambda csvRow: csvRow[0]);
    sortedList_forUsersFollowing = sorted(initialSortedList, key = lambda csvRow: csvRow[1]);
        # order ids (followed_user_id, referenceUser) for the users the referenceUser is following, 
        # i.e. [(18, 1), (19, 1), ... (292, 1), (16, 2), ..., (295, 300)]
            # both columns sorted, priority second column

    sortedList_forUsersFollowedBy = sorted(sortedList_forUsersFollowing, key = lambda csvRow: csvRow[0]);
        # order ids (followed_user_id, reference_user) for the users the referenceUser is followED by, 
        # i.e. [(1,3), (1, 13), ..., (1, 297), (2, 16), (2, 51), ..., (300, 275), (300, 280)]
            # both coulmns sorted, priority first column

csvReadFile.close();

# check
'''
with open('sortedForuser_following_id.csv', 'w') as csvOutFileColumnTwo:

    csvOutFileColumnTwo.write('user_being_followed_id, user_following_id\n');

    for row in sortedList_forUsersFollowing:
        csvOutFileColumnTwo.write(f'{row[0]}, {row[1]}\n');

csvOutFileColumnTwo.close();

with open('sortedForuser_being_followed_id.csv', 'w') as csvOutFileColumnOne:

    csvOutFileColumnOne.write('user_being_followed_id, user_following_id\n');

    for row in sortedList_forUsersFollowedBy:
        csvOutFileColumnOne.write(f'{row[0]}, {row[1]}\n');


csvOutFileColumnOne.close();
'''

with open('user_followers_followedBy_noSQL.csv', 'w') as csvOutFile:

    csvOutFile.write('user_id, user_follows, user_followers\n');

    for i in range(1, 301):
        
        userFollowsList = [userFollows for (userID, userFollows) in sortedList_forUsersFollowing if userID == i];
        userFollowersList = [userFollowers for (userFollowers, userID) in sortedList_forUsersFollowedBy if userID == i];

        # user_follows is 'user_following_id' column (2nd) priority sorted,
            # i.e. (18, 1), (19, 1), ..., (292, 1), (16, 2), ...,
            # sortedList_forUsersFollowing
            # generate 1: [18, 19, ..., 292], 2: [16, ...]

        # user_followers (followedBy) is `user_being_following_id` column (1st) priority sorted, 
            # i.e. (1, 3), (1, 13), (1, 15), ... (1, 297), (2, 16), 
            # sortedList_forUsersFollowedBy
            # generate 1: [3, 13, 15, 25, 51, 94, 126, ..., 297], 2: [16, ...]

        # print(f'{i}: {userFollowsList}')
        # print(f'{i}: {userFollowersList}')

        # experience note: basically if it is a uni-directional relationship that could be modeled as a many-to-many relationship, probably nosql is more convenient?
            # i.e. thinking about "block": it should go both ways (although the initiator is stored so it could be removed), therefore SQL rel
            # thinking about "likes": there is a definitive parent relationship

            # revision: nosql is good for sibling relationships that are uni-directional if there exists a relation between the two.
                # nosql is ideal for optional information

            # sql is good for sibling directional, and parent-chijld relationships.
            # in this case, as for "following" and "followers", the involved entities are siblings but they are independent.
                # with nosql, it is O(1)*nlog(n) searching, for a population of N to search and n subpopulations
                # with sql, it would be Nlog(N), at best and MAYBE Nlog(N)*n = n(N^2)log(N) 

        # csvOutFile.write(f'{i}, {userFollowsList}, {userFollowersList}\n');

csvOutFile.close();
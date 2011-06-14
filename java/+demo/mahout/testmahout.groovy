/*
grouplens data in the paper
user, item, rating
1,1,1
1,2,5
1,4,2
1,5,4
2,1,4
2,2,2
2,4,5
2,5,1
2,6,2
3,1,2
3,2,4
3,3,3
3,6,5
4,1,2
4,2,4
4,4,5
4,5,1

 */

import org.apache.mahout.cf.taste.impl.model.file.FileDataModel
import org.apache.mahout.cf.taste.impl.neighborhood.NearestNUserNeighborhood
import org.apache.mahout.cf.taste.impl.recommender.GenericItemBasedRecommender
import org.apache.mahout.cf.taste.impl.recommender.GenericUserBasedRecommender
import org.apache.mahout.cf.taste.impl.similarity.PearsonCorrelationSimilarity
import org.apache.mahout.cf.taste.model.DataModel
import org.apache.mahout.cf.taste.neighborhood.UserNeighborhood
import org.apache.mahout.cf.taste.similarity.ItemSimilarity
import org.apache.mahout.cf.taste.similarity.UserSimilarity

def User2User() {
    DataModel model = new FileDataModel(new File("data.txt"));
    UserSimilarity userSimilarity = new PearsonCorrelationSimilarity(model);
    //userSimilarity.setPreferenceInferrer(new AveragingPreferenceInferrer());
    UserNeighborhood neighborhood = new NearestNUserNeighborhood(10, userSimilarity, model);
    GenericUserBasedRecommender recommender = new GenericUserBasedRecommender(model, neighborhood, userSimilarity);
    //Recommender cachingRecommender = new CachingRecommender(recommender);
    //List<RecommendedItem> recommendations = cachingRecommender.recommend(1234, 10);

    // result should be 4.56 according to the paper
    // doesn't turn out to be 4.56: could be the PearsonCorrelation uses the missing data differently.
    println recommender.estimatePreference(1, 6)
}

def Item2Item() {
    DataModel model = new FileDataModel(new File("data.txt"));
    //Collection<GenericItemSimilarity.ItemItemSimilarity> correlations = ...;
    //ItemSimilarity itemSimilarity = new GenericItemSimilarity(correlations);
    ItemSimilarity itemSimilarity = new PearsonCorrelationSimilarity(model);
    GenericItemBasedRecommender recommender = new GenericItemBasedRecommender(model, itemSimilarity);
    //Recommender cachingRecommender = new CachingRecommender(recommender);
    //List<RecommendedItem> recommendations = cachingRecommender.recommend(1234, 10);
    println recommender.estimatePreference(1, 6)
}



Item2Item()
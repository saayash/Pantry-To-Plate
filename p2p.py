import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional

# Data classes for our recipe system
class Ingredient:
    def __init__(self, name: str):
        self.name = name

class Nutrition:
    def __init__(self, calories: float, carbs: float, protein: float, fat: float, 
                 fiber: float, sugar: float, sodium: float, calcium: float,
                 iron: float, vitamin_c: float, folate: float):
        self.calories = calories
        self.carbs = carbs
        self.protein = protein
        self.fat = fat
        self.fiber = fiber
        self.sugar = sugar
        self.sodium = sodium
        self.calcium = calcium
        self.iron = iron
        self.vitamin_c = vitamin_c
        self.folate = folate

class Recipe:
    def __init__(self, name: str, ingredients: List[Ingredient], diet: str, 
                 prep_time: int, cook_time: int, flavor_profile: str, course: str,
                 nutrition: Nutrition, youtube_link: str, healthy: str):
        self.name = name
        self.ingredients = ingredients
        self.diet = diet
        self.prep_time = prep_time
        self.cook_time = cook_time
        self.flavor_profile = flavor_profile
        self.course = course
        self.nutrition = nutrition
        self.youtube_link = youtube_link
        self.healthy = healthy

class RecipeBook:
    def __init__(self, csv_path: str = "p2p.csv"):
        self.recipes = self._load_from_csv(csv_path)
    
    def _load_from_csv(self, csv_path: str):
        df = pd.read_csv(csv_path)
        recipes = []

        for row in df.index:
            ingredients = [Ingredient(name.strip()) 
                          for name in df['ingredients'][row].split(",")]
            
            nutrition = Nutrition(
                calories=df['Calories (kcal)'][row],
                carbs=df['Carbohydrates (g)'][row],
                protein=df['Protein (g)'][row],
                fat=df['Fats (g)'][row],
                fiber=df['Fibre (g)'][row],
                sugar=df['Free Sugar (g)'][row],
                sodium=df['Sodium (mg)'][row],
                calcium=df['Calcium (mg)'][row],
                iron=df['Iron (mg)'][row],
                vitamin_c=df['Vitamin C (mg)'][row],
                folate=df['Folate (µg)'][row]
            )
            
            recipe = Recipe(
                name=df['Dish Name'][row],
                ingredients=ingredients,
                diet=df['diet'][row],
                prep_time=df['prep_time'][row],
                cook_time=df['cook_time'][row],
                flavor_profile=df['flavor_profile'][row],
                course=df['course'][row],
                nutrition=nutrition,
                youtube_link=df['youtube_link'][row],
                healthy=df['healthy/unhealthy'][row]
            )
            recipes.append(recipe)
        
        return recipes
    
    def search_by_ingredients(self, ingredients: List[str]):
        matching_recipes = []
        for recipe in self.recipes:
            recipe_ingredients = [ingri.name.lower() for ingri in recipe.ingredients]
            if all(ingri.lower() in recipe_ingredients for ingri in ingredients):
                matching_recipes.append(recipe)
        return matching_recipes
    
    def search_by_name(self, name: str):
        name = name.lower()
        for recipe in self.recipes:
            if name in recipe.name.lower():
                return recipe
        return None
    
    def get_all_recipes(self):
        return self.recipes
    
    def filter_recipes(self, recipes: List[Recipe], filter_type: str, ascending: bool = True):
        if filter_type == "time":
            return sorted(recipes, key=lambda x: x.prep_time + x.cook_time, reverse=not ascending)
        elif filter_type == "calories":
            return sorted(recipes, key=lambda x: x.nutrition.calories, reverse=not ascending)
        elif filter_type == "ingredients":
            return sorted(recipes, key=lambda x: len(x.ingredients), reverse=not ascending)
        return recipes
    
    def get_unique_ingredients(self):
        ingredients = set()
        for recipe in self.recipes:
            for ingri in recipe.ingredients:
                ingredients.add(ingri.name)
        return sorted(ingredients)
    
    def get_unique_diets(self):
        return sorted(list(set(recipe.diet for recipe in self.recipes)))
    
    def get_unique_flavors(self):
        return sorted(list(set(recipe.flavor_profile for recipe in self.recipes)))
    
    def get_unique_courses(self):
        return sorted(list(set(recipe.course for recipe in self.recipes)))
    
    def get_health_categories(self):
        return ["healthy", "unhealthy"]

class RecipeApp:
    def __init__(self):
        self.recipe_book = RecipeBook()
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "home"
        if 'selected_recipe' not in st.session_state:
            st.session_state.selected_recipe = None
        if 'selected_ingredients' not in st.session_state:
            st.session_state.selected_ingredients = []
        if 'selected_diet' not in st.session_state:
            st.session_state.selected_diet = "All"
        if 'selected_flavor' not in st.session_state:
            st.session_state.selected_flavor = "All"
        if 'selected_course' not in st.session_state:
            st.session_state.selected_course = "All"
        if 'selected_health' not in st.session_state:
            st.session_state.selected_health = "All"
    
    def display_home_page(self):
        st.title("Pantry To Plate (P2P)")
        st.write("Welcome to the Recipe Finder app! Select an option below:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 Search Ingredients"):
                st.session_state.current_page = "search_ingredients"
                st.rerun()
            if st.button("📚 Recipe Book"):
                st.session_state.current_page = "recipe_book"
                st.rerun()
        
        with col2:
            if st.button("📊 Analyze"):
                st.session_state.current_page = "analyze"
                st.rerun()
            if st.button("ℹ️ About Us"):
                st.session_state.current_page = "about"
                st.rerun()
    
    def display_search_ingredients_page(self):
        st.title("Search by Ingredients")
        
        st.session_state.selected_ingredients = st.multiselect(
            "Select ingredients you have:",
            self.recipe_book.get_unique_ingredients()
        )
        
        if st.session_state.selected_ingredients:
            matching_recipes = self.recipe_book.search_by_ingredients(st.session_state.selected_ingredients)
            
            st.subheader("Filter Options")
            
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            with filter_col1:
                time_filter = st.selectbox("Filter by Time", ["None", "Low to High", "High to Low"])
                if time_filter != "None":
                    ascending = time_filter == "Low to High"
                    matching_recipes = self.recipe_book.filter_recipes(matching_recipes, "time", ascending)
            
            with filter_col2:
                calorie_filter = st.selectbox("Filter by Calories", ["None", "Low to High", "High to Low"])
                if calorie_filter != "None":
                    ascending = calorie_filter == "Low to High"
                    matching_recipes = self.recipe_book.filter_recipes(matching_recipes, "calories", ascending)
            
            with filter_col3:
                ingredient_filter = st.selectbox("Filter by Number of Ingredients", ["None", "Low to High", "High to Low"])
                if ingredient_filter != "None":
                    ascending = ingredient_filter == "Low to High"
                    matching_recipes = self.recipe_book.filter_recipes(matching_recipes, "ingredients", ascending)
            
            filter_col4, filter_col5, filter_col6 = st.columns(3)
            with filter_col4:
                st.session_state.selected_diet = st.selectbox("Filter by Diet", ["All"] + self.recipe_book.get_unique_diets())
                if st.session_state.selected_diet != "All":
                    matching_recipes = [r for r in matching_recipes if r.diet == st.session_state.selected_diet]
            
            with filter_col5:
                st.session_state.selected_flavor = st.selectbox("Filter by Flavor Profile", ["All"] + self.recipe_book.get_unique_flavors())
                if st.session_state.selected_flavor != "All":
                    matching_recipes = [r for r in matching_recipes if r.flavor_profile == st.session_state.selected_flavor]
            
            with filter_col6:
                st.session_state.selected_course = st.selectbox("Filter by Course", ["All"] + self.recipe_book.get_unique_courses())
                if st.session_state.selected_course != "All":
                    matching_recipes = [r for r in matching_recipes if r.course == st.session_state.selected_course]
            
            # Split into healthy and unhealthy
            healthy_recipes = [r for r in matching_recipes if r.healthy == "healthy"]
            unhealthy_recipes = [r for r in matching_recipes if r.healthy == "unhealthy"]
            
            # Display healthy recipes
            st.subheader("🥗 Healthy Options")
            if healthy_recipes:
                for recipe in healthy_recipes:
                    total_time = recipe.prep_time + recipe.cook_time
                    if st.button(f"{recipe.name} ({recipe.diet}, {total_time} mins, {recipe.nutrition.calories:.0f} cal)", key=f"healthy_{recipe.name}"):
                        st.session_state.selected_recipe = recipe
                        st.session_state.current_page = "recipe_detail"
                        st.rerun()
            else:
                st.info("No healthy recipes found with these filters.")
            
            # Display unhealthy recipes
            st.subheader("🍔 Unhealthy Options")
            if unhealthy_recipes:
                for recipe in unhealthy_recipes:
                    total_time = recipe.prep_time + recipe.cook_time
                    if st.button(f"{recipe.name} ({recipe.diet}, {total_time} mins, {recipe.nutrition.calories:.0f} cal)", key=f"unhealthy_{recipe.name}"):
                        st.session_state.selected_recipe = recipe
                        st.session_state.current_page = "recipe_detail"
                        st.rerun()
            else:
                st.info("No unhealthy recipes found with these filters.")
        else:
            st.info("Please select some ingredients to find matching recipes.")
        
        if st.button("Back to Home"):
            st.session_state.current_page = "home"
            st.rerun()
    
    def display_recipe_book_page(self):
        st.title("Recipe Book")
        
        search_term = st.text_input("Search for a recipe by name:")
        
        if search_term:
            matching_recipes = [r for r in self.recipe_book.get_all_recipes() if search_term.lower() in r.name.lower()]
        else:
            matching_recipes = self.recipe_book.get_all_recipes()
        
        st.subheader("Filter Options")
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
        
        with filter_col1:
            st.session_state.selected_diet = st.selectbox("Filter by Diet", ["All"] + self.recipe_book.get_unique_diets())
            if st.session_state.selected_diet != "All":
                matching_recipes = [r for r in matching_recipes if r.diet == st.session_state.selected_diet]
        
        with filter_col2:
            st.session_state.selected_flavor = st.selectbox("Filter by Flavor Profile", ["All"] + self.recipe_book.get_unique_flavors())
            if st.session_state.selected_flavor != "All":
                matching_recipes = [r for r in matching_recipes if r.flavor_profile == st.session_state.selected_flavor]
        
        with filter_col3:
            st.session_state.selected_course = st.selectbox("Filter by Course", ["All"] + self.recipe_book.get_unique_courses())
            if st.session_state.selected_course != "All":
                matching_recipes = [r for r in matching_recipes if r.course == st.session_state.selected_course]
        
        with filter_col4:
            st.session_state.selected_health = st.selectbox("Filter by Health", ["All"] + self.recipe_book.get_health_categories())
            if st.session_state.selected_health != "All":
                matching_recipes = [r for r in matching_recipes if r.healthy == st.session_state.selected_health]
        
        st.subheader("All Recipes")
        for recipe in matching_recipes:
            total_time = recipe.prep_time + recipe.cook_time
            health_icon = "🥗" if recipe.healthy == "healthy" else "🍔"
            if st.button(f"{health_icon} {recipe.name} ({recipe.diet}, {total_time} mins, {recipe.nutrition.calories:.0f} cal)", key=recipe.name):
                st.session_state.selected_recipe = recipe
                st.session_state.current_page = "recipe_detail"
                st.rerun()
        
        if st.button("Back to Home"):
            st.session_state.current_page = "home"
            st.rerun()
    
    def display_recipe_detail_page(self):
        if not st.session_state.selected_recipe:
            st.warning("No recipe selected.")
            st.session_state.current_page = "home"
            st.rerun()
            return
        
        recipe = st.session_state.selected_recipe
        st.title(recipe.name)
        
        health_status = "🥗 Healthy" if recipe.healthy == "healthy" else "🍔 Unhealthy"
        st.subheader(health_status)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Diet", recipe.diet)
        with col2:
            st.metric("Prep Time", f"{recipe.prep_time} mins")
        with col3:
            st.metric("Cook Time", f"{recipe.cook_time} mins")
        with col4:
            st.metric("Flavor", recipe.flavor_profile.capitalize())
        
        st.subheader(f"Course: {recipe.course}")
        
        st.subheader("Nutritional Information (per serving)")
        nut_col1, nut_col2, nut_col3 = st.columns(3)
        with nut_col1:
            st.metric("Calories", f"{recipe.nutrition.calories:.0f} kcal")
            st.metric("Protein", f"{recipe.nutrition.protein:.1f} g")
        with nut_col2:
            st.metric("Carbs", f"{recipe.nutrition.carbs:.1f} g")
            st.metric("Fiber", f"{recipe.nutrition.fiber:.1f} g")
        with nut_col3:
            st.metric("Fat", f"{recipe.nutrition.fat:.1f} g")
            st.metric("Sugar", f"{recipe.nutrition.sugar:.1f} g")
        
        st.subheader("Ingredients")
        for ingredient in recipe.ingredients:
            st.write(f"- {ingredient.name}")

        st.subheader("Video Tutorial")
        if recipe.youtube_link and pd.notna(recipe.youtube_link):
            st.video(recipe.youtube_link)
        else:
            st.info("No video available for this recipe")
        
        st.subheader("Macronutrient Distribution")
        labels = ['Protein', 'Carbs', 'Fat']
        sizes = [recipe.nutrition.protein, recipe.nutrition.carbs, recipe.nutrition.fat]
        
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)
        
        st.subheader("Micronutrients (100 gm)")
        micronutrients = {
            'Sodium': recipe.nutrition.sodium,
            'Calcium': recipe.nutrition.calcium,
            'Iron': recipe.nutrition.iron,
            'Vitamin C': recipe.nutrition.vitamin_c,
            'Folate': recipe.nutrition.folate
        }
        
        fig, ax = plt.subplots()
        ax.bar(micronutrients.keys(), micronutrients.values())
        plt.xticks(rotation=45)
        st.pyplot(fig)
        
        if st.button("Back"):
            st.session_state.current_page = "recipe_book" if "book" in st.session_state.current_page else "search_ingredients"
            st.rerun()
    
    def display_analyze_page(self):
        st.title("Recipe Analysis")
        
        # Basic statistics
        total_recipes = len(self.recipe_book.get_all_recipes())
        veg_recipes = len([r for r in self.recipe_book.get_all_recipes() if r.diet == "vegetarian"])
        non_veg_recipes = total_recipes - veg_recipes
        healthy_recipes = len([r for r in self.recipe_book.get_all_recipes() if r.healthy == "healthy"])
        unhealthy_recipes = total_recipes - healthy_recipes
        
        st.subheader("Recipe Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Recipes", total_recipes)
        with col2:
            st.metric("Vegetarian", veg_recipes)
        with col3:
            st.metric("Non-Vegetarian", non_veg_recipes)
        with col4:
            st.metric("Healthy vs Unhealthy", f"{healthy_recipes} 🥗 / {unhealthy_recipes} 🍔")
        
        # Average nutrition values
        avg_calories = sum(r.nutrition.calories for r in self.recipe_book.get_all_recipes()) / total_recipes
        avg_protein = sum(r.nutrition.protein for r in self.recipe_book.get_all_recipes()) / total_recipes
        avg_carbs = sum(r.nutrition.carbs for r in self.recipe_book.get_all_recipes()) / total_recipes
        avg_fat = sum(r.nutrition.fat for r in self.recipe_book.get_all_recipes()) / total_recipes
        
        st.subheader("Average Nutritional Values")
        nut_col1, nut_col2, nut_col3, nut_col4 = st.columns(4)
        with nut_col1:
            st.metric("Calories", f"{avg_calories:.1f} kcal")
        with nut_col2:
            st.metric("Protein", f"{avg_protein:.1f} g")
        with nut_col3:
            st.metric("Carbs", f"{avg_carbs:.1f} g")
        with nut_col4:
            st.metric("Fat", f"{avg_fat:.1f} g")
        
        # 1. Course distribution pie chart
        st.subheader("Course Distribution")
        course_counts = {}
        for recipe in self.recipe_book.get_all_recipes():
            course_counts[recipe.course] = course_counts.get(recipe.course, 0) + 1
        
        fig1, ax1 = plt.subplots()
        ax1.pie(course_counts.values(), labels=course_counts.keys(), autopct='%1.1f%%')
        ax1.axis('equal')
        st.pyplot(fig1)
        
        # 2. Nutrient Comparison by Course
        st.subheader("Nutrient Content by Course Type")
        courses = {}
        for recipe in self.recipe_book.get_all_recipes():
            if recipe.course not in courses:
                courses[recipe.course] = {'count': 0, 'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}

            courses[recipe.course]['count'] += 1
            courses[recipe.course]['calories'] += recipe.nutrition.calories
            courses[recipe.course]['protein'] += recipe.nutrition.protein
            courses[recipe.course]['carbs'] += recipe.nutrition.carbs
            courses[recipe.course]['fat'] += recipe.nutrition.fat
        
        for course in courses:
            courses[course]['calories'] /= courses[course]['count']
            courses[course]['protein'] /= courses[course]['count']
            courses[course]['carbs'] /= courses[course]['count']
            courses[course]['fat'] /= courses[course]['count']
        
        course_names = list(courses.keys())
        calories = [courses[course]['calories'] for course in course_names]
        protein = [courses[course]['protein'] for course in course_names]
        carbs = [courses[course]['carbs'] for course in course_names]
        fat = [courses[course]['fat'] for course in course_names]
        
        x = np.arange(len(course_names))
        width = 0.2
        
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        ax2.bar(x - width*1.5, calories, width, label='Calories (kcal)')
        ax2.bar(x - width/2, protein, width, label='Protein (g)')
        ax2.bar(x + width/2, carbs, width, label='Carbs (g)')
        ax2.bar(x + width*1.5, fat, width, label='Fat (g)')
        
        ax2.set_xlabel('Course Type')
        ax2.set_ylabel('Amount')
        ax2.set_title('Average Nutrient Content by Course')
        ax2.set_xticks(x)
        ax2.set_xticklabels(course_names)
        ax2.legend()
        plt.xticks(rotation=45)
        st.pyplot(fig2)
        
        # 3. Macronutrient Balance Comparison (Stacked Bar Chart)
        st.subheader("Average Macronutrient Balance")
        
        # Calculate averages
        healthy_avg = {
            'protein': np.mean([r.nutrition.protein for r in self.recipe_book.get_all_recipes() if r.healthy == "healthy"]),
            'carbs': np.mean([r.nutrition.carbs for r in self.recipe_book.get_all_recipes() if r.healthy == "healthy"]),
            'fat': np.mean([r.nutrition.fat for r in self.recipe_book.get_all_recipes() if r.healthy == "healthy"])
        }
        
        unhealthy_avg = {
            'protein': np.mean([r.nutrition.protein for r in self.recipe_book.get_all_recipes() if r.healthy == "unhealthy"]),
            'carbs': np.mean([r.nutrition.carbs for r in self.recipe_book.get_all_recipes() if r.healthy == "unhealthy"]),
            'fat': np.mean([r.nutrition.fat for r in self.recipe_book.get_all_recipes() if r.healthy == "unhealthy"])
        }
        
        categories = ['Healthy', 'Unhealthy']
        protein = [healthy_avg['protein'], unhealthy_avg['protein']]
        carbs = [healthy_avg['carbs'], unhealthy_avg['carbs']]
        fat = [healthy_avg['fat'], unhealthy_avg['fat']]
        
        fig3, ax3 = plt.subplots(figsize=(8, 6))
        ax3.bar(categories, protein, label='Protein', color='#1f77b4')
        ax3.bar(categories, carbs, bottom=protein, label='Carbs', color='#ff7f0e')
        ax3.bar(categories, fat, bottom=[i+j for i,j in zip(protein, carbs)], label='Fat', color='#2ca02c')
        
        ax3.set_ylabel('Grams per serving')
        ax3.set_title('Macronutrient Composition Comparison')
        ax3.legend()
        st.pyplot(fig3)
        
        if st.button("Back to Home"):
            st.session_state.current_page = "home"
            st.rerun()
    
    def display_about_page(self):
        st.title("About Us")
        st.write("""
        ### Recipe Finder App
        This application helps you find recipes based on ingredients you have available.
        
        **Features:**
        - Search recipes by ingredients with healthy/unhealthy categorization
        - Browse full recipe book with filters
        - View detailed nutritional information
        - Analyze recipe statistics with visualizations
        
        **Data Source:**
        - Indian Food Dataset
        
        Developed by: Afnan, Ayesha
        """)
        
        if st.button("Back to Home"):
            st.session_state.current_page = "home"
            st.rerun()
    
    def run(self):
        if st.session_state.current_page == "home":
            self.display_home_page()
        elif st.session_state.current_page == "search_ingredients":
            self.display_search_ingredients_page()
        elif st.session_state.current_page == "recipe_book":
            self.display_recipe_book_page()
        elif st.session_state.current_page == "recipe_detail":
            self.display_recipe_detail_page()
        elif st.session_state.current_page == "analyze":
            self.display_analyze_page()
        elif st.session_state.current_page == "about":
            self.display_about_page()

def main():
    st.set_page_config(page_title="P2P", layout="centered")
    app = RecipeApp()
    app.run()

if __name__ == "__main__":
    main()
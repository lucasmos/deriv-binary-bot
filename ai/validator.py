import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report, confusion_matrix
from ..bot.utils.logger import get_logger

logger = get_logger('ai.validator')

class WalkForwardValidator:
    def __init__(self, n_splits=5, test_size=0.2):
        self.n_splits = n_splits
        self.test_size = test_size
        self.tscv = TimeSeriesSplit(
            n_splits=n_splits,
            test_size=test_size
        )
        
    def validate(self, model, X, y):
        """Perform walk-forward validation on the model"""
        results = []
        
        for train_index, test_index in self.tscv.split(X):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            
            # Train model on this fold
            model.train(X_train, y_train)
            
            # Evaluate on test set
            y_pred = model.model.predict(X_test).argmax(axis=1)
            y_true = y_test.argmax(axis=1)
            
            # Calculate metrics
            report = classification_report(
                y_true, y_pred,
                target_names=['buy', 'sell', 'hold'],
                output_dict=True
            )
            
            cm = confusion_matrix(y_true, y_pred)
            
            results.append({
                'accuracy': report['accuracy'],
                'precision': report['weighted avg']['precision'],
                'recall': report['weighted avg']['recall'],
                'f1_score': report['weighted avg']['f1-score'],
                'confusion_matrix': cm,
                'train_samples': len(X_train),
                'test_samples': len(X_test)
            })
        
        # Aggregate results
        aggregated = {
            'mean_accuracy': np.mean([r['accuracy'] for r in results]),
            'mean_f1': np.mean([r['f1_score'] for r in results]),
            'details': results
        }
        
        logger.info(f"Walk-forward validation completed. Mean accuracy: {aggregated['mean_accuracy']:.2%}")
        return aggregated
    
    def cross_validate(self, model, X, y, n_runs=3):
        """Multiple runs of walk-forward validation for more reliable results"""
        all_results = []
        
        for run in range(n_runs):
            logger.info(f"Starting validation run {run + 1}/{n_runs}")
            results = self.validate(model, X, y)
            all_results.append(results)
            
        # Calculate statistics across runs
        mean_accuracy = np.mean([r['mean_accuracy'] for r in all_results])
        std_accuracy = np.std([r['mean_accuracy'] for r in all_results])
        
        return {
            'mean_accuracy': mean_accuracy,
            'std_accuracy': std_accuracy,
            'runs': all_results
        }
import os
from flask import Flask, request, redirect, url_for, render_template, Response
from flask.views import MethodView, View

# Configuration etc.
#-----------------------------------------
app = Flask(__name__)
app.config.update({'SECRET_KEY': os.urandom(24)})
app.config.update(dict(
                    DEBUG=True,
                    SECRET_KEY='development key'))

IMAGE_DIR = 'static/images'
RESULTS_FILE = 'results.txt'

all_images_in_dir = set([fname for fname in os.listdir(IMAGE_DIR)
                         if os.path.isfile(os.path.join(IMAGE_DIR, fname))])

if os.path.isfile(RESULTS_FILE):
    with open(RESULTS_FILE) as f:
        labeled_images = set([row.split('\t')[0] for row in f])
else:
    labeled_images = set()

unlabeled_images = all_images_in_dir - labeled_images

# Views
#-----------------------------------------

class LabelImageView(MethodView):
    template = 'label_image.html'

    def get_multiple_choice(self, form):
        return {col[0]: form[col[0]] for col in MULTIPLE_CHOICE_COLUMNS}

    def get(self, img_id=None):
        if not len(unlabeled_images):
            return redirect(url_for('display_stats'))
        next_img = next(iter(unlabeled_images))
        return render_template(self.template, next_img=next_img)

    def post(self, img_id=None):
        label = request.form['label']
        fname = request.form['fname']
        with open(RESULTS_FILE, 'a') as f:
            f.write('{0}\t{1}\n'.format(fname,label))
        unlabeled_images.remove(fname)
        return self.get()

class StatsView(View):
    template = 'display_stats.html'

    def dispatch_request(self):
        stats = {}
        with open(RESULTS_FILE) as f:
            for row in f:
                fname, label = row.strip().split('\t')
                stats[label] = stats.get(label, 0) + 1
        stats['recall'] = float(stats.get('tp', 0)) / (stats.get('tp', 0) + stats.get('fn', 0))
        stats['precision'] = float(stats.get('tp', 0)) / (stats.get('tp', 0) + stats.get('fp',0))
        stats['f1_score'] = 2*(stats['precision']*stats['recall'])/(stats['precision']+stats['recall'])
        return render_template(
                self.template,
                stats=stats
        )

# Routing
#-----------------------------------------
label_image = LabelImageView.as_view('label_image')
display_stats = StatsView.as_view('display_stats')

app.add_url_rule('/',
                 view_func=label_image)
app.add_url_rule('/stats',
                 view_func=display_stats)

if __name__ == "__main__":
     app.run()
